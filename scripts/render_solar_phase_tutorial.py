"""Execute the small solar-phase tutorial and save its single figure."""

from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/solar-phase.md"
    path = root / "docs/_static/tutorials/solar/solar-phase-two-antennas.png"
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
    assert data.vis.shape == (4, 3072, 1)
    print("Returned visibility bytes:", data.vis.nbytes)
    print("Saved:", path)


if __name__ == "__main__":
    main()
