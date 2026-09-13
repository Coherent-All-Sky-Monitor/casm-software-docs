"""Execute selected displayed snippets offline, in bounded subprocesses.

Default: verify and render to a temporary directory. --render updates tutorial
PNGs. Raw voltage data are optional unless --require-voltage is supplied.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "voltage": ("read-voltages", None, "io/voltage-single-stream.png"),
    "rank1": ("rank1-diagnostics", [0], "calibration/rank1-primary.png"),
    "transit": ("check-calibration", [0], "transit/cyga-light-curve.png"),
    "imaging": ("image-visibilities", [0], "imaging/allsky-saved.png"),
    "injection": ("injection-recovery", [0], None),
}


def worker(name, output):
    # VoltageReader maps the entire on-disk file, but touches only selected
    # samples. Cap resident memory in the parent; allow that virtual mapping.
    if name != "voltage":
        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    page, selection, figure = CASES[name]
    path = ROOT / f"docs/guides/{page}.md"
    blocks = re.findall(r"^```python\n(.*?)^```", path.read_text(), re.M | re.S)
    saved = []

    def show():
        assert figure and not saved, "Unexpected figure count"
        target = Path(output) / figure
        target.parent.mkdir(parents=True, exist_ok=True)
        plt.gcf().savefig(target, dpi=150, bbox_inches="tight")
        plt.close("all")
        saved.append(str(target))

    plt.show = show
    namespace = {"__name__": "__tutorial__"}
    for index in range(len(blocks)) if selection is None else selection:
        exec(compile(blocks[index], f"{path}:block{index + 1}", "exec"), namespace)
    source_root = Path(os.environ["CASM_TUTORIAL_SOURCE_ROOT"]).resolve()
    for module_name, module in tuple(sys.modules.items()):
        if module_name.split(".")[0] in {
            "casm_io", "casm_imaging", "casm_vis_analysis", "casm_calibrator",
            "bf_weights_generator", "casm_t2", "casm_t3",
        } and getattr(module, "__file__", None):
            assert Path(module.__file__).resolve().is_relative_to(source_root), module.__file__
    assert len(saved) == int(figure is not None)
    if name == "voltage":
        result = namespace["result"]
        assert list(result.voltages) == [0]
        assert result.voltages[0].shape == (305, 512, 12)
        assert not result.filled_subbands
        assert namespace["corr"].vis.shape[2:] == (2, 2)
    elif name == "rank1":
        assert namespace["ratio"].shape == (3072,)
    elif name == "transit":
        assert namespace["power"].shape == (136,)
    elif name == "injection":
        assert namespace["shot"]["outcome"] == "recovered"
    print(f"PASS {name}; peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.1f} MiB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--require-voltage", action="store_true")
    parser.add_argument("--source-root", type=Path, default=ROOT.parent)
    parser.add_argument("--worker", choices=CASES)
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.output)
        return
    manifest = json.loads((ROOT / "tutorial-inputs.json").read_text())
    for item in manifest["retained_inputs"] + manifest["figures"]:
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], path
    voltage = Path(manifest["voltage"]["path"])
    if voltage.is_file():
        assert voltage.stat().st_size == manifest["voltage"]["bytes"]
        with voltage.open("rb") as stream:
            assert hashlib.sha256(stream.read(4096)).hexdigest() == manifest["voltage"]["header_sha256"]
    source_paths = [args.source_root / p for p in (
        "casm_io", "casm_vis_analysis/src", "casm_calibrator/src",
        "bf_weights_generator", "casm-bf-imaging", "casm_t2", "casm_t3",
    )]
    assert all(p.is_dir() for p in source_paths[:5]), "Supply isolated source worktrees"
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(map(str, source_paths)),
               CASM_TUTORIAL_SOURCE_ROOT=str(args.source_root.resolve()),
               PYTHONDONTWRITEBYTECODE="1", MPLBACKEND="Agg", CASM_IO_WORKERS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1", BLIS_NUM_THREADS="1")
    with tempfile.TemporaryDirectory(prefix="casm-tutorial-") as tmp:
        env["MPLCONFIGDIR"] = tmp
        output = str(ROOT / "docs/_static/tutorials") if args.render else tmp
        for name in CASES:
            if name == "voltage" and not Path(manifest["voltage"]["path"]).is_file():
                if args.require_voltage:
                    raise FileNotFoundError(manifest["voltage"]["path"])
                print("SKIP voltage: historical raw dump missing", flush=True)
                continue
            process = subprocess.Popen(
                [sys.executable, __file__, "--worker", name, "--output", output],
                cwd=ROOT, env=env,
            )
            deadline = time.monotonic() + 90
            try:
                while process.poll() is None:
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"{name}: exceeded 90 seconds")
                    try:
                        status = Path(f"/proc/{process.pid}/status").read_text()
                    except FileNotFoundError:
                        continue
                    rss = re.search(r"^VmRSS:\s+(\d+)", status, re.M)
                    if rss and int(rss[1]) >= 900 * 1024:
                        raise MemoryError(f"{name}: exceeded 900 MiB resident cap")
                    time.sleep(0.05)
                if process.returncode:
                    raise subprocess.CalledProcessError(process.returncode, process.args)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
            figure = CASES[name][2]
            if figure and not args.render:
                from PIL import Image, ImageChops
                with Image.open(Path(output) / figure) as actual, Image.open(
                    ROOT / "docs/_static/tutorials" / figure
                ) as expected:
                    assert actual.size == expected.size, figure
                    assert ImageChops.difference(actual.convert("RGB"), expected.convert("RGB")).getbbox() is None, figure
    print("PASS retained input hashes; illustrative/live blocks intentionally excluded")


if __name__ == "__main__":
    main()
