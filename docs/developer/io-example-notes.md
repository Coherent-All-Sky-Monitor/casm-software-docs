# I/O tutorial sources and verification

The beginner guides use existing CASM readers and plotting functions. Their
short examples require user-supplied files and have not been run on observation
data during this documentation task. Existing figures were visually inspected
and copied without editing or rerunning their analysis.

## Source snapshot

- `casm_io`: `22ef826d9f2ba355388523265081da1468e5a4ff`.
- `casm_vis_analysis`: `5039eb4714b5c62eb72b6b8f82527c787ca4f214`.
- `read_visibilities`, `VisibilityReader`, baseline selection:
  `/home/casm/software/dev/casm_io/casm_io/correlator/`.
- Voltage reader and correlator:
  `/home/casm/software/dev/casm_io/casm_io/voltage/reader.py` and `correlate.py`.
- Plotting API:
  `/home/casm/software/dev/casm_vis_analysis/src/casm_vis_analysis/plotting/autocorr.py`.

## Visibility figure

Source PNG:
`/mnt/nvme5/casm_pipeline/scratchpad/output/range_2026-08-05_05-20-00_to_2026-08-05_10-30-00/autocorr/autocorr_snap0.png`.
Copy: `docs/_static/tutorials/io/visibility-snap0.png`.
Both SHA-256: `78bde76faaaf28b7c3e87a2387ff203975f9ed2c804fb1c927234d07b5bb1d62`.

The figure labels six SNAP 0 inputs, 2026-08-05 05:20:16–10:29:31 UTC, in
instrumental power dB. Its path and format match the `run_autocorr` invocation
in `/mnt/nvme5/casm_pipeline/scratchpad/cyga_stationary_beam.py`, which requests
05:20–10:30 UTC and calls the package's `plot_autocorr` through the runner.
Script SHA-256: `23003ec1bc8ab7729f63977ba2fa02fbd4d0add1cd9610bc28ae7a419049087a`.
No execution manifest survives alongside the PNG to prove the exact producing
revision; this attribution follows the matching source call and output path.

Only the autocorrelation figure is reused. The historical script's later
steering, private CSV parsing and antenna-number assumptions are not tutorial
instructions. The beginner example selects two inputs, while the archived plot
contains six and spans a longer interval. It is not its newly generated output.

## Cross-correlation phase figure

Source: `/mnt/nvme5/vishnu/cal_build_20260824/figs/phase_raw_sawtooth_aug23_exact512_CAL0823N.png`.
Copy: `docs/_static/tutorials/io/cross-phase-sawtooth.png`, unchanged.
The matching `cal_aug23_exact512_CAL0823N_diagnostics.ipynb` displays this
figure in cell 5. `bf_weights_generator/recipe_diagnostics.py:plot_sawtooth`
averages complex visibilities over the selected times before taking their
angle, masking excluded frequencies. The recipe supplies static-subtracted
visibilities. Thus "raw" in the figure means before fringe-stopping, not
untouched correlator output. This is a historical multi-baseline illustration,
not a claimed execution of the beginner's single-integration snippet.

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
two copies are now retained in the documentation repository with their origins.
