"""Execute the Cyg A calibration-check tutorial and save its single figure.

Reads the full correlator triangle for a two-hour transit: about 29 GB peak
resident, so this runs outside the bounded-tutorial harness.
"""

from pathlib import Path
import re
import resource
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/check-calibration.md"
    path = root / "docs/_static/tutorials/transit/cyga-beam-power.png"
    blocks = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    namespace = {"__name__": "__tutorial__"}
    started = time.monotonic()

    def save_figure():
        assert len(plt.get_fignums()) == 1
        plt.gcf().savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

    plt.show = save_figure
    for index, code in enumerate(blocks):
        exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)

    data = namespace["data"]
    result = namespace["result"]
    assert data.vis.shape[1:] == (3072, 8256)          # full triangle, full band
    assert 45 <= data.vis.shape[0] <= 60
    assert not data.metadata.get("gaps")
    assert not data.metadata.get("missing_files")
    assert set(result["power"]) == {"Cyg A", "off-source"}
    assert result["n_chan_used"] == 2425
    print("Files:", data.metadata.get("files"))
    print("Integrations:", data.vis.shape[0], "bytes:", data.vis.nbytes)
    print(f"Wall time: {time.monotonic() - started:.1f} s")
    print("Peak RSS (GB):",
          round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 1))
    print("Saved:", path)


if __name__ == "__main__":
    main()
