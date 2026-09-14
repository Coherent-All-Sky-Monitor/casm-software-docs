"""Execute the beam-dump-to-filterbank tutorial blocks and save its figure.

Runs every ```python block of docs/guides/beamdump-to-filterbank.md in order in
one namespace, exactly as printed, and saves the single figure the last block
produces. The page prints an archive output directory for the converted .fil;
set CASM_BEAMDUMP_FIL_DIR to the directory holding aug16_b03.fil and that one
path string is substituted before exec. Block file, beam and sample range are
unchanged.

Prerequisite (run once, outside this script):

    casm-beamdump-to-fil \\
        '/mnt/nvme4/data/casm/beam_dumps/beam_0-63_2026-08-16-03:22:43.dat.*' \\
        --out-dir $CASM_BEAMDUMP_FIL_DIR --prefix aug16 --name 3=b03
"""

import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAGE_FIL_DIR = "/mnt/nvme3/vishnu/aug16/fil"


def main():
    root = Path(__file__).resolve().parents[1]
    page = root / "docs/guides/beamdump-to-filterbank.md"
    path = root / "docs/_static/tutorials/filterbank/beamdump-quicklook.png"
    path.parent.mkdir(parents=True, exist_ok=True)

    fil_dir = os.environ.get("CASM_BEAMDUMP_FIL_DIR", PAGE_FIL_DIR)
    text = page.read_text().replace(PAGE_FIL_DIR, fil_dir)
    blocks = re.findall(r"^```python\n(.*?)^```", text, re.M | re.S)
    assert len(blocks) == 3, f"expected 3 python blocks, found {len(blocks)}"
    namespace = {"__name__": "__tutorial__"}

    def save_figure():
        assert len(plt.get_fignums()) == 1
        plt.gcf().savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

    plt.show = save_figure
    for index, code in enumerate(blocks):
        exec(compile(code, f"{page}:block{index + 1}", "exec"), namespace)

    fb = namespace["fb"]
    cb = namespace["cb"]
    # per-beam .fil: a header nbeams above 1 is the pre-2026-08-19 corr1 bug
    assert fb.nbeams == 1, f"header nbeams is {fb.nbeams}, not 1"
    assert fb.nchans == 3072
    assert namespace["nsamp"] == fb.nsamples, "memmap sample count disagrees"
    assert cb.nsamples == namespace["nsamp_30s"]
    assert namespace["img"].shape[1] == 3072
    print("Source .fil:", namespace["fil"])
    print("Cutout samples:", cb.nsamples, "bins:", namespace["img"].shape[0])
    print("Saved:", path)


if __name__ == "__main__":
    main()
