"""Freeze small existing tutorial products; never run during a site build."""
import json
from pathlib import Path
import sqlite3
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "docs/_static/tutorials"


def main():
    source = Path("/mnt/nvme5/casm_pipeline/scratchpad/cyga_stationary_beam_20260805.npz")
    with np.load(source, allow_pickle=False) as saved:
        np.savez(STATIC / "transit/cyga-light-curve.npz",
                 time_unix=saved["time_unix"], lc=saved["lc"])
    connection = sqlite3.connect(
        "file:/mnt/nvme5/casm_pipeline/db/t2.sqlite?mode=ro", uri=True, timeout=5,
    )
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT file_id, inject_utc, beam, dm, inject_snr, rec_snr, rec_dm, "
            "rec_beam, outcome, fail_reason FROM injections WHERE file_id IN (?, ?)",
            ("inj_20260913_0023", "inj_20260913_0021"),
        ).fetchall()
    finally:
        connection.close()
    assert len(rows) == 2
    (STATIC / "injections/frozen-records.json").write_text(
        json.dumps({r["file_id"]: dict(r) for r in rows}, indent=2) + "\n")
    print("Frozen light curve and two read-only ledger records")


if __name__ == "__main__":
    main()
