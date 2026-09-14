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
has a 90-second deadline, one I/O worker and one BLAS/OpenMP thread. A Linux
resident-memory watchdog stops it at 900 MiB. Non-voltage processes also have
a 1 GiB address-space limit. VoltageReader maps the entire file virtually;
its measured peak resident memory was 166 MiB. Imaging redraw peaked at
151 MiB; other checks at 73 MiB or less. This is not part of the Sphinx build.

`tutorial-inputs.json` records retained input hashes, selection and verification
boundaries. Missing raw voltage data prints SKIP unless `--require-voltage` is
used. Saved rank-1, transit, image and injection examples need no scratch data.
Live SQLite and illustrative new-analysis blocks are intentionally excluded.
The visibility and solar figures retain their prior verified provenance and
were not regenerated in this audit.

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

- `calibration/rank1-primary.npz`: byte copy of
  `/mnt/nvme5/solar0819/recipe_demo_20260820/rank1_vs_freq_20260820.npz`.
- `transit/cyga-light-curve.npz`: exact `time_unix` and `lc` arrays from
  `/mnt/nvme5/casm_pipeline/scratchpad/cyga_stationary_beam_20260805.npz`.
  Original SHA256: `c38928b7ccfd68266aa01e3ab736791ed1afe63fdd2dfae5f47b40aa2d33ae7d`.
- `imaging/allsky-saved.npz`: byte copy of
  `/mnt/nvme3/casm_monitor/figures/imaging/frames/1789299471.npz`, 165,054 bytes.
- `injections/frozen-records.json`: selected fields for ledger shots 0023/0021,
  read with SQLite `mode=ro`, independent of mutable archive paths.

`scripts/prepare_bounded_products.py` documents extraction of the two derived
records. It is an explicit refresh operation, not a check. The injection PNG
is the existing byte-preserved replay; its archive hash and event identity
remain in [injection notes](injection-example-notes.md).

The all-sky product contains image, axes, timestamp, predicted source markers
and a configuration fingerprint. It does not contain the raw visibility,
calibration bytes or dated layout. Its image is nonnegative; no signed-image
interpretation or flux calibration is inferred from this redraw. Historical
June-28 source-centred figures remain separate. Reconstructing either original
calculation needs missing runtime/input provenance; neither was rerun.

## Execution source evidence

The retained figures were first rendered with casm_io `73279e93` and
casm-bf-imaging `6203e0d3`. Pixel-identical redraws were verified on
2026-09-14 UTC against clean isolated revisions casm_io
`c6e463f91b1f14e4c0def47c006af6bc019025fe` and casm-bf-imaging
`04c1610ebba4a98b1df480915466a84a902703e5`. The execution files below
were unchanged. These checks do not execute a calibration solve or test its
handling of visibility validity, subset identities or masked NaNs; those
require the calibrator's separate correctness tests before science deployment.
Execution file SHA256 identities:

```text
cd8b6cbe00a4c7aa4aced6af1e9f965407a162cc82ef9c98ffc648921a770dd2  casm_io/casm_io/voltage/reader.py
471af763a5b9000bdd41a1a5b97ea6381b5e5043d116fb6ae415694a8f732c61  casm_io/casm_io/voltage/correlate.py
33653a76f163e9550dc2e16137a7ab3a2a858ebd81ba54e41804a34395fae1dd  casm-bf-imaging/casm_imaging/imaging/allsky.py
```

No full calibration, fold, acquisition, service action, source edit or
production documentation change was performed for these examples.

`scripts/check_tutorial_browser.py` checks the five affected local HTML pages
at 1440- and 390-pixel widths, including loaded figures and horizontal overflow.
It uses file URLs, without contacting the production preview. Both widths
passed; screenshots are under `_build/tutorial-screenshots/`.
