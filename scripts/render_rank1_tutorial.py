"""Execute the rank-1 tutorial and save its two figures.

Reads an hour of solar visibilities (5.3 GB), so run it on the correlator
host. The Python blocks are executed exactly as displayed, in one namespace,
from a scratch directory: the displayed ``plot_svd_vs_freq`` call writes a
relative path.
"""

from pathlib import Path
import os
import re
import resource
import shutil
import tempfile
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def peak_rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/rank1-diagnostics.md"
    out_dir = root / "docs/_static/tutorials/calibration"
    rank1_png = out_dir / "rank1-vs-freq.png"
    svd_png = out_dir / "svd-vs-freq.png"
    blocks = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    namespace = {"__name__": "__tutorial__"}

    def save_figure():
        assert len(plt.get_fignums()) == 1
        plt.gcf().savefig(rank1_png, dpi=150, bbox_inches="tight")
        plt.close()

    plt.show = save_figure
    started = time.time()
    with tempfile.TemporaryDirectory() as scratch:
        os.chdir(scratch)
        for index, code in enumerate(blocks):
            t0 = time.time()
            exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)
            print(f"block{index + 1}: {time.time() - t0:.1f} s, "
                  f"peak RSS {peak_rss_gb():.1f} GB", flush=True)
        shutil.copyfile(Path(scratch) / "svd-vs-freq.png", svd_png)

    cal = namespace["cal"]
    ratio = namespace["ratio"]
    assert len(cal["ant_ids"]) == 16
    assert cal["rank1_ratios"].shape == (3072,)
    assert int(namespace["fs"]["time_mask"].sum()) == 26
    print("rank-1 median:", float(namespace["np"].nanmedian(ratio)))
    print("svd stats:", namespace["stats"])
    print("Saved:", rank1_png, svd_png)
    print(f"Wall {time.time() - started:.1f} s, peak RSS {peak_rss_gb():.1f} GB")


if __name__ == "__main__":
    main()
