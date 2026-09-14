"""Execute the cross-day phase tutorial and save its single figure."""

from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/cross-day-phase.md"
    path = root / "docs/_static/tutorials/phase/cross-day-phase.png"
    blocks = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    namespace = {"__name__": "__tutorial__"}

    def save_figure():
        assert len(plt.get_fignums()) == 1
        plt.gcf().savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

    plt.show = save_figure
    for index, code in enumerate(blocks):
        exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)
    data = namespace["data"]
    assert data.vis.shape[1:] == (3072, 15)
    assert 20 <= data.vis.shape[0] <= 35
    assert not data.metadata.get("gaps")
    assert not data.metadata.get("missing_files")
    # One figure only: 4 baselines is under plot_phase_vs_freq's split_max.
    assert len(namespace["figs"]) == 1
    print("Files:", data.metadata.get("files"))
    print("Saved:", path)


if __name__ == "__main__":
    main()
