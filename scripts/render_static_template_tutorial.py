"""Execute the off-source static template tutorial and save its figures."""

from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGURES = [
    "quiet-window-altitudes.png",
    "template-vs-deployed.png",
    "sun-baseline-before-after.png",
]


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/static-template.md"
    out_dir = root / "docs/_static/tutorials/static"
    out_dir.mkdir(parents=True, exist_ok=True)
    blocks = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    namespace = {"__name__": "__tutorial__"}
    saved = []

    def save_figure():
        assert len(plt.get_fignums()) == 1
        path = out_dir / FIGURES[len(saved)]
        plt.gcf().savefig(path, dpi=150, bbox_inches="tight")
        plt.close("all")
        saved.append(path)

    plt.show = save_figure
    for index, code in enumerate(blocks):
        exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)

    static = namespace["static"]
    assert static["static_vis"].shape == (3072, 8256)
    assert "data" not in static                      # quiet-window cube released
    assert namespace["sun"].vis.shape == (4, 3072, 8256)
    assert len(saved) == len(FIGURES)
    print("Quiet window (UTC):", static["window_unix"])
    print("Amplitude ratio (5/50/95):",
          namespace["np"].percentile(namespace["ratio"], [5, 50, 95]))
    for path in saved:
        print("Saved:", path)


if __name__ == "__main__":
    main()
