# I/O tutorial sources and verification

The visibility tutorial's displayed Python blocks were executed on the CASM
host on 2026-09-13, producing its two figures. The voltage figure remains an
archived illustration; its beginner snippets have not been executed. Source
packages were not edited and no acquisition commands were run.

## Source snapshot

- `casm_io`: `22ef826d9f2ba355388523265081da1468e5a4ff`.
- `casm_vis_analysis`: `5039eb4714b5c62eb72b6b8f82527c787ca4f214`.
- `read_visibilities`, `VisibilityReader`, baseline selection:
  `/home/casm/software/dev/casm_io/casm_io/correlator/`.
- Voltage reader and correlator:
  `/home/casm/software/dev/casm_io/casm_io/voltage/reader.py` and `correlate.py`.
- Plotting API:
  `/home/casm/software/dev/casm_vis_analysis/src/casm_vis_analysis/plotting/autocorr.py`.

## Matched visibility figures

`scripts/render_visibility_tutorial.py` executes every Python block in
`docs/guides/read-visibilities.md` in order, replacing only `plt.show()` with
a PNG save using Agg. It contains no separate data-selection or analysis code.
Run manually with the shared environment, `CASM_IO_WORKERS=1`, BLAS threads
limited to one, and `timeout 90s`. It is not part of the site build.

Read root: `/mnt/nvme4/data/casm`. Discovery selected
`visibilities_64ant/2026-08-23-19:18:14.dat.1` for the requested
20:42–20:52 UTC window. Returned data are `(4, 3072, 3)` complex64,
294,912 bytes, with no reported gaps or missing files. Actual integration
timestamps span 20:42:59–20:49:51 UTC. Frequencies descend from 484.375
to 390.655517578125 MHz. The historical August-7 layout maps antennas 9/19
to packet inputs 8/18. This is also the layout recorded by the Aug-23
calibration recipe in `/mnt/nvme5/vishnu/cal_build_20260824/params_aug23_exact512.json`.

- `docs/_static/tutorials/io/visibility-two-antennas.png`: time-averaged
  autos from the displayed `plot_autocorr` call. SHA256:
  `9637805c0d10133d1e264b0f7ec1cb79213d14d177660758c37a58410774b08e`.
- `docs/_static/tutorials/io/cross-amplitude-phase.png`: amplitude and
  wrapped phase of the first integration. SHA256:
  `b5f526dfacba613a02731dd4621651b08b67d30e17e0dfa209a93cede1b35a51`.

Both plots were visually checked. The phase has a clear wrapped slope, with
narrow-band departures. No background subtraction, RFI masking, calibration
or fringe stopping was applied. An initial four-integration August-19 trial
was noise-dominated; it is not the example now shown.

## Voltage figure

Source notebook:
`/home/casm/software/dev/casm_io/examples/voltage_quickstart.ipynb`.
Notebook SHA-256: `66b859ca939fb1e7952a6439281be206f2532737fd80598ccfcbac0422804fd9`.
The first PNG output in zero-based cell 13 was base64-decoded directly to
`docs/_static/tutorials/io/voltage-snap0.png`.
PNG SHA-256: `f59b30b912cba35a67e667faf5641a4ccb14ce1d4914dea0d64c45d915097636`.

Cells 7 and 9 read voltage samples; cell 9 accumulates squared real and imaginary
components. Cell 13 divides by sample count and plots one logarithmic panel per
ADC. Its title gives August 3, 11:06:52–11:06:54 PDT. Cell 9 records 61,037
samples, streams 0/3/4/5 zero-filled, with useful data in streams 1–2.

The notebook is not a sequential execution record: the earlier acquisition cell
prints a different time and all six gathered streams, while cell 7 finds only
streams 1–2. The figure is reused only to teach its plotted quantity and layout.
Its exact raw dump identity is not asserted. Acquisition and cleanup cells were
not run or copied into the tutorial. The live notebook can trigger dumps and
delete files; opening it should not be followed by an indiscriminate Run All.

## Reader details kept out of the first walkthrough

- The introductory read uses `data_root="/mnt/nvme4/data/casm"` discovery and header-derived
  format, with UTC and descending frequency defaults. Current 64-antenna
  recordings do not require an explicit format. This is not a hardcoded
  64-antenna fallback: headerless files need `fmt`. The upstream CLAUDE.md's
  narrower default root is stale; the inspected signature defaults to `/mnt`.
- The top-level `read_visibilities(inputs=...)` returns the subset but drops
  `metadata['inputs']` and `nsig_subset` during stitching. The guide keeps its
  sorted input list explicitly. For two inputs the triangle is `[00, 01, 11]`.
- `ref`/`targets` cannot request autocorrelations: targets must not include ref.
  The guide uses `inputs` so both autos and the cross arrive in one read.
- `triu_flat_index` lives in `casm_io.correlator.baselines`, not the correlator
  package initializer. A larger subset uses ranks within the sorted selection.
- Current header-bearing data supply their format; old headerless files need
  an explicitly verified format. The upstream format table has stale durations.
  The shipped 64-antenna JSON has 137.438953472 s integrations, 32 per file.
- Channel or baseline selection takes the memory-mapped path. The upstream
  documented boundary `OverflowError` remains a known issue, not a tutorial fix.
- Returned frequencies, not legacy band constants, should label every plot.
  Frequency selections and channel-index selections are mutually exclusive.
- An explicit worker count takes precedence over `CASM_IO_WORKERS` in source.
- Voltage correlation returns a full square input matrix, unlike the flattened
  triangle from the on-disk visibility reader. `tint_s` rounds to whole voltage
  samples; final incomplete bins are dropped. `time_s` is bin-centre relative time.

The scratchpad viewer at
`/home/casm/software/casm_analysis_tools/webconsole/pages/3_Scratchpad.py` treats
figures as temporary and exposes adjacent captions/scripts when present. These
archived voltage copy is retained in the documentation repository with its origin.
