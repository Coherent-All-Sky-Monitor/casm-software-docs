"""Check the exact source combination without installing or running services.

The release manifest is deliberately separate from the three-package API
snapshot. It covers the other workflow dependencies too. Pass --record only
after reviewing and committing source changes; --check is read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "casm_io": ("casm_io", "."),
    "casm_vis_analysis": ("casm_vis_analysis", "src"),
    "casm_calibrator": ("casm_calibrator", "src"),
    "bf_weights_generator": ("bf_weights_generator", "."),
    "casm_t2": ("casm_t2", "."),
    "casm_t3": ("casm_t3", "."),
    "casm-bf-imaging": ("casm_imaging", "."),
    "casm_beam_scheduler": ("casm_beam_scheduler", "src"),
    "casm_offline_frb_injector": ("casm_offline_frb_injector", "."),
    "casm_monitor": ("casm_monitor", "."),
}
SOURCE_ONLY = ("casm_hella_vishnu",)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def describe(source_root: Path) -> dict:
    packages = {}
    for name in (*PACKAGES, *SOURCE_ONLY):
        repo = source_root / name
        if git(repo, "status", "--porcelain", "--untracked-files=no"):
            raise ValueError(f"{name}: commit reviewed tracked changes before verification")
        hashes = {}
        for relative in git(repo, "ls-files").splitlines():
            path = repo / relative
            # Source, configuration, packaging and tests; do not hash multi-GB
            # scientific example outputs or private files outside Git.
            if path.suffix in {".py", ".toml", ".yaml", ".yml", ".json", ".sh",
                               ".cu", ".cuh", ".cpp", ".h", ".cmake", ".cfg"} or relative in {"CMakeLists.txt", "version.txt"}:
                if not path.resolve().is_relative_to(repo.resolve()):
                    raise ValueError(f"{name}/{relative}: external source symlink")
                hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        packages[name] = {"revision": git(repo, "rev-parse", "HEAD"), "files": hashes}
    return {"schema": 1, "packages": packages}


def check_imports(source_root: Path) -> None:
    paths = [str(source_root / name / subdir) for name, (_, subdir) in PACKAGES.items()]
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(paths), PYTHONDONTWRITEBYTECODE="1",
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    code = """
import importlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1]).resolve()
for repo, (module, _) in json.loads(sys.argv[2]).items():
    imported = importlib.import_module(module)
    origin = pathlib.Path(imported.__file__).resolve()
    if not origin.is_relative_to(root / repo):
        raise RuntimeError(f'{module} imported outside candidate: {origin}')
    print(f'{module}: {origin}')
"""
    subprocess.run([sys.executable, "-B", "-c", code, str(source_root), json.dumps(PACKAGES)],
                   env=env, cwd=ROOT, check=True, timeout=60)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    current = describe(source_root)
    check_imports(source_root)
    manifest = ROOT / "release-sources.json"
    if args.record:
        manifest.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(f"Recorded {len(current['packages'])} committed source repositories")
    else:
        expected = json.loads(manifest.read_text())
        if current != expected:
            changed = [name for name in (*PACKAGES, *SOURCE_ONLY)
                       if current["packages"][name] != expected["packages"].get(name)]
            raise SystemExit("Release source drift: " + ", ".join(changed))
        print(f"OK: {len(current['packages'])} revisions and source hashes; "
              f"{len(PACKAGES)} isolated Python imports")


if __name__ == "__main__":
    main()
