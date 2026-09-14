# Bounded tutorial execution

The voltage, rank-1, Cyg A light curve and saved all-sky figures were rendered
on 2026-09-13 by executing the displayed Python blocks. The runner replaces
only `plt.show()` with a PNG save. The frozen injection block was executed
against the retained JSON. No second science recipe is implemented here.

From the documentation checkout root:

```bash
/home/casm/software/dev/casm_venvs/casm_offline_env/bin/python scripts/check_bounded_tutorials.py --require-voltage
```

Default output goes to a temporary directory. `--render` deliberately refreshes
the four matching figures. Default checks also compare rendered pixels with
the retained PNGs. `--source-root` selects sibling isolated source
worktrees; imports use their paths without shared installs. Each subprocess
runs with one I/O worker and one BLAS/OpenMP thread and a fixed deadline. This
is not part of the Sphinx build.

`tutorial-inputs.json` records retained input hashes and selection. Missing
raw voltage data prints SKIP unless `--require-voltage` is used. Saved rank-1,
transit, image and injection examples need no scratch data. Live SQLite and
illustrative new-analysis blocks are excluded. The visibility and solar
figures keep their own provenance sections on their tutorial pages; do not
regenerate them from here.

## Voltage selection

Input: `/mnt/nvme4/data/casm/cand_dumps/stream_1/2026-08-02-14:32:06_0205375108055040.000000.dada`.
File size: 4,152,365,056 bytes. Only its 4096-byte header and selected samples
were inspected; no full-file hash or raw copy was made. The parser reports
`DUMP_UTC_START=2026-08-03-18:11:41.810`, `TSAMP=32.768`, `NCHAN=512`,
`RESOLUTION=67584`. The observation's `UTC_START` is August 2 and is not the
dump start. Legacy frequency and antenna-count header fields do not override
the maintained reader's stream geometry.

Exactly 305 samples, stream 1 and SNAP 0, return `(305, 512, 12)` complex64,
14,991,360 bytes, descending 468.75–453.155517578125 MHz, no filled streams.
The ADC-0 mean-power figure uses all these times and channels. The displayed
correlation returns `(9, 512, 2, 2)` with 31 samples per bin. The historical
twelve-panel figure remains preserved; its mixed-run raw identity is unresolved.

## Saved products

Retained paths below are under `docs/_static/tutorials/`:

- `imaging/allsky-saved.npz`: byte copy of
  `/mnt/nvme3/casm_monitor/figures/imaging/frames/1789299471.npz`, 165,054 bytes.
- `injections/frozen-records.json`: selected fields for ledger shots 0023/0021,
  read with SQLite `mode=ro`, independent of mutable archive paths.

`scripts/prepare_bounded_products.py` documents extraction of the two derived
records. It is an explicit refresh operation, not a check. The injection PNG
is the existing byte-preserved replay; its archive path and event identity
are in the [injection tutorial's provenance section](../guides/injection-recovery.md#provenance).

The all-sky product contains image, axes, timestamp, predicted source markers
and a configuration fingerprint. It does not contain the raw visibility,
calibration bytes or dated layout. Its image is nonnegative; no signed-image
interpretation or flux calibration is inferred from this redraw. Historical
June-28 source-centred figures remain separate. Reconstructing either original
calculation needs missing runtime/input provenance; neither was rerun.

## Execution source evidence

Pixel-identical redraws were verified against clean isolated checkouts of
casm_io and casm-bf-imaging. These checks do not execute a calibration solve
or test its handling of visibility validity, subset identities or masked
NaNs; those require the calibrator's separate correctness tests before
science deployment. Source revisions and file hashes: `source-snapshot.json`
in the repository.

No full calibration, fold, acquisition, service action, source edit or
production documentation change was performed for these examples.

`scripts/check_tutorial_browser.py` checks the five affected local HTML pages
at 1440- and 390-pixel widths, including loaded figures and horizontal overflow.
It uses file URLs, without contacting the production preview. Both widths
passed; screenshots are under `_build/tutorial-screenshots/`.

## Full-data tutorials

Six tutorials read tens of GB from `/mnt/nvme4` and are rendered by their own
scripts, outside the bounded harness: `render_rank1_tutorial.py`,
`render_cyga_tutorial.py`, `render_static_template_tutorial.py`,
`render_cross_day_phase_tutorial.py`, `render_rfi_delay_tutorial.py` and
`render_beamdump_tutorial.py`. Each executes the page's displayed blocks in one
namespace, asserts the shapes stated on the page, and writes the PNGs listed in
`tutorial-inputs.json`. Run them from a directory outside `software/dev`.
