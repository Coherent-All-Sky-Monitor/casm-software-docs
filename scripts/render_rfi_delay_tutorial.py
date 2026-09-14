"""Execute the RFI-mask and delay tutorial and save its two figures."""

from pathlib import Path
import re
import resource
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/rfi-and-delay.md"
    out_dir = root / "docs/_static/tutorials/delay"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Saved in the order the page calls plt.show().
    paths = [out_dir / "rfi-mask-spectrum.png",
             out_dir / "delay-phase-vs-freq.png"]
    blocks = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    namespace = {"__name__": "__tutorial__"}
    saved = []

    def save_figure():
        assert len(plt.get_fignums()) == 1
        path = paths[len(saved)]
        plt.gcf().savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        saved.append(path)

    plt.show = save_figure
    start = time.time()
    for index, code in enumerate(blocks):
        exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)

    data, fs = namespace["data"], namespace["fs"]
    params = namespace["params"]
    assert data.vis.shape[1:] == (3072, 8256)
    assert 6 <= data.vis.shape[0] <= 10
    assert not data.metadata.get("gaps")
    assert not data.metadata.get("missing_files")
    assert int(data["freq_mask"].sum()) == 308
    assert len(fs["target_aids"]) == 23
    assert len(saved) == len(paths)
    print("Integrations:", data.vis.shape[0],
          "flagged channels:", int(data["freq_mask"].sum()))
    print("Files:", data.metadata.get("files"))
    print("Max |delay|:", float(abs(params["delay_ns"]).max()), "ns")
    print("Wall time: %.1f s" % (time.time() - start))
    print("Peak memory: %.1f GB"
          % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    for path in saved:
        print("Saved:", path)


if __name__ == "__main__":
    main()
