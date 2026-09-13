"""Render the two visibility tutorial figures by executing its Python blocks.

Run explicitly on the CASM host; not part of a documentation build. Reads only
the small historical selection stated in the page. No telescope operations.
"""

from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/read-visibilities.md"
    output = root / "docs/_static/tutorials/io"
    blocks = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    names = iter(("visibility-two-antennas.png", "cross-amplitude-phase.png"))
    saved = []

    def save_figure():
        path = output / next(names)
        plt.gcf().savefig(path, dpi=150, bbox_inches="tight")
        saved.append(path)
        plt.close()

    plt.show = save_figure
    namespace = {"__name__": "__tutorial__"}
    for index, code in enumerate(blocks):
        exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)
    assert len(saved) == 2, "The tutorial must produce exactly two figures"
    data = namespace["data"]
    assert data.vis.shape[2] == 3
    assert data.vis.shape[0] <= 10
    print("Integration times (Unix UTC):", data.time_unix)
    print("Returned visibility bytes:", data.vis.nbytes)
    print("Read metadata:", data.metadata)
    print("Saved:", *saved, sep="\n")


if __name__ == "__main__":
    main()
