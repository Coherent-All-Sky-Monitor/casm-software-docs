"""Offline wheel smoke in copied source trees and a fresh dependency-inheriting venv.

Run with the shared offline Python, --source-root AUDIT_ROOT, --output NEW_DIR,
and --dependencies SHARED_SITE_PACKAGES. Builds use --no-deps and
--no-build-isolation in copies; installation targets only NEW_DIR/venv.
Candidate probes append the shared dependency directory without executing its
.pth files. This verifies installation with inherited dependencies, not a
hermetic dependency solve or the advertised minimum Python version.

Entrypoints are loaded, never called. Imports may use only the named read-only
font/platform helpers, temporary files under NEW_DIR, and /dev/null. Network,
database connections, other subprocesses and outside writes are rejected.
--reprobe checks the already installed wheels without rebuilding changed source.
report.json preserves before/after source hashes and flags source races.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import zipfile

REPOS = (
    "casm_io", "casm_vis_analysis", "casm_calibrator", "bf_weights_generator",
    "casm-bf-imaging", "casm_t2", "casm_t3", "casm_monitor",
    "casm_beam_scheduler", "casm_offline_frb_injector",
)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def snapshot(root, destination=None):
    names = sorted(set(git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")) - {""})
    files = {}
    for name in names:
        path = root / name
        if not path.exists():
            files[name] = "deleted"
            continue
        if path.is_symlink():
            raise ValueError(f"Review source symlink before copying: {path}")
        data = path.read_bytes()
        files[name] = hashlib.sha256(data).hexdigest()
        if destination:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            shutil.copymode(path, target)
    return {"head": git(root, "rev-parse", "HEAD").decode().strip(),
            "status": git(root, "status", "--porcelain=v1").decode(),
            "files": files,
            "tree_sha256": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}


def probe(args):
    # Append dependencies as a plain path: never execute their editable .pth files.
    sys.path.append(args.dependencies)
    import importlib.metadata as metadata
    import importlib
    import sysconfig
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet
    import platform

    output = args.output.resolve()
    site = Path(sysconfig.get_paths()["purelib"]).resolve()
    assert site.is_relative_to(output), site
    helpers = []

    def protect(event, values):
        if event == "subprocess.Popen":
            argv = values[1]
            if argv in (["uname", "-p"], ["fc-list", "--help"], ["fc-list", "--format=%{file}\\n"]):
                helpers.append(argv)
            else:
                raise RuntimeError(f"Import attempted subprocess: {values[:2]}")
        if event in {"socket.connect", "socket.bind", "os.system", "sqlite3.connect"}:
            raise RuntimeError(f"Import attempted forbidden operation: {event}")
        if event == "open":
            path, mode, flags = values
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            if writing and not isinstance(path, int) and str(path) != os.devnull and not Path(path).resolve().is_relative_to(output):
                raise RuntimeError(f"Import attempted write outside smoke directory: {path}")
        if event in {"os.mkdir", "os.remove", "os.rmdir", "os.rename"}:
            if not Path(values[0]).resolve().is_relative_to(output):
                raise RuntimeError(f"Import attempted mutation outside smoke directory: {event}")

    sys.addaudithook(protect)
    report = {"distribution": args.distribution, "entrypoints": [], "requirements": [], "errors": []}
    dist = metadata.distribution(args.distribution)
    report["version"] = dist.version
    report["metadata_path"] = str(dist._path)
    assert Path(dist._path).resolve().is_relative_to(site)
    wheel = next((output / "wheels").glob(args.distribution.replace("-", "_") + "-*.whl"))
    verified = 0
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.endswith("/") or name.endswith(".dist-info/RECORD"):
                continue
            installed = Path(dist.locate_file(name)).resolve()
            assert installed.is_relative_to(site), installed
            assert installed.read_bytes() == archive.read(name), installed
            verified += 1
    report["wheel_files_verified"] = verified
    report["requires_python"] = dist.metadata.get("Requires-Python")
    assert platform.python_version() in SpecifierSet(report["requires_python"])
    report["requires_dist"] = dist.requires or []
    for text in dist.requires or []:
        req = Requirement(text)
        if req.marker and not req.marker.evaluate({"extra": ""}):
            continue
        try:
            found = metadata.distribution(req.name)
            ok = found.version in req.specifier
            row = {"requirement": text, "version": found.version, "metadata_path": str(found._path), "ok": ok}
        except metadata.PackageNotFoundError:
            row = {"requirement": text, "ok": False, "error": "missing dependency"}
        report["requirements"].append(row)
        if not row["ok"]:
            report["errors"].append(row)
    expected = tomllib.loads((output / "sources" / args.repo / "pyproject.toml").read_text())["project"]
    assert set(expected.get("dependencies", [])) <= set(dist.requires or [])
    if args.repo == "casm_t2":
        assert report["requires_python"] == ">=3.11"
        assert any(Requirement(r).name == "astropy" for r in dist.requires or [])
    for ep in dist.entry_points:
        if ep.group != "console_scripts":
            continue
        row = {"name": ep.name, "target": ep.value}
        try:
            function = ep.load()  # Resolve only. NEVER call the entrypoint.
            module = importlib.import_module(ep.module)
            origin = Path(module.__file__).resolve()
            assert origin.is_relative_to(site), origin
            assert callable(function)
            launcher = output / "venv/bin" / ep.name
            assert launcher.is_file()
            assert str(output / "venv/bin/python") in launcher.read_text().splitlines()[0]
            row.update(ok=True, module_path=str(origin))
        except Exception as exc:
            row.update(ok=False, error=f"{type(exc).__name__}: {exc}")
            report["errors"].append(row)
        report["entrypoints"].append(row)
    report["candidate_modules"] = {}
    report["allowed_import_helpers"] = helpers
    for name, module in tuple(sys.modules.items()):
        if name.split(".")[0] in {r.replace("-", "_") for r in REPOS} | {"casm_imaging"}:
            origin = getattr(module, "__file__", None)
            if origin:
                report["candidate_modules"][name] = origin
                assert Path(origin).resolve().is_relative_to(site), origin
    (output / f"probe-{args.repo}.json").write_text(json.dumps(report, indent=2) + "\n")
    print(args.repo, "PASS" if not report["errors"] else "FAIL", len(report["entrypoints"]), "entrypoints", flush=True)
    if report["errors"]:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dependencies", required=True)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--reprobe", action="store_true")
    parser.add_argument("--repo")
    parser.add_argument("--distribution")
    args = parser.parse_args()
    if args.probe:
        probe(args)
        return
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "tmp").mkdir(exist_ok=True)
    assert args.reprobe or not (output / "venv").exists(), "Use a fresh output directory"
    report = {"environment": "Fresh candidate venv; shared dependency site appended without .pth processing. Not hermetic.",
              "shared_dependencies": args.dependencies, "python": sys.version, "packages": {}}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1",
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", MPLBACKEND="Agg",
               MPLCONFIGDIR=str(output / "mpl"), XDG_CACHE_HOME=str(output / "cache"), TMPDIR=str(output / "tmp"))
    env.pop("PYTHONPATH", None)
    if args.reprobe:
        report = json.loads((output / "report.json").read_text())
    else:
        for name in REPOS:
            report["packages"][name] = {"before": snapshot(args.source_root / name, output / "sources" / name)}
        (output / "source-before.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(command, log, timeout=90):
        with (output / log).open("w") as stream:
            try:
                result = subprocess.run(command, cwd=output, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
                return result.returncode
            except subprocess.TimeoutExpired:
                return "timeout"

    if not args.reprobe:
        assert run([sys.executable, "-m", "venv", str(output / "venv")], "venv.log") == 0
    wheels = output / "wheels"
    wheels.mkdir(exist_ok=True)
    for name in () if args.reprobe else REPOS:
        result = report["packages"][name]
        result["build_exit"] = run([sys.executable, "-m", "pip", "wheel", "--no-index", "--no-deps",
                                   "--no-build-isolation", "--no-cache-dir", "--wheel-dir", str(wheels),
                                   str(output / "sources" / name)], f"build-{name}.log")
        print(name, "build", result["build_exit"], flush=True)
    wheel_files = sorted(wheels.glob("*.whl"))
    report["wheels"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in wheel_files}
    python = str(output / "venv/bin/python")
    if not args.reprobe:
        report["install_exit"] = run([python, "-m", "pip", "install", "--no-index", "--no-deps", *map(str, wheel_files)], "install.log")
    for name in REPOS:
        result = report["packages"][name]
        if result["build_exit"] != 0 or report["install_exit"] != 0:
            continue
        project = tomllib.loads((output / "sources" / name / "pyproject.toml").read_text())["project"]
        result["probe_exit"] = run([python, "-I", str(Path(__file__).resolve()), "--probe", "--source-root", str(args.source_root),
                                   "--output", str(output), "--dependencies", args.dependencies, "--repo", name,
                                   "--distribution", project["name"]], f"probe-{name}.log")
        path = output / f"probe-{name}.json"
        if path.exists():
            result["probe"] = json.loads(path.read_text())
        print(name, "probe", result["probe_exit"], flush=True)
    for name, result in report["packages"].items():
        result["after"] = snapshot(args.source_root / name)
        result["source_changed"] = result["before"] != result["after"]
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Report:", output / "report.json", flush=True)
    if report["install_exit"] != 0 or any(
        r["build_exit"] != 0 or r.get("probe_exit") != 0 or r.get("probe", {}).get("errors")
        for r in report["packages"].values()
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
