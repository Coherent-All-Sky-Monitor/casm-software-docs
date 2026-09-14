# From visibilities to 512 calibrated beams

Follow one existing calibration run from the measured visibilities to its saved
beam weights. The example uses the August 23, 2026 Sun observation, a matched
nighttime static template, 16 antennas, and an exact 512-beam grid.

The [original diagnostic notebook](../_static/tutorials/calibration-walkthrough/cal_aug23_exact512_CAL0823N_diagnostics.ipynb)
displays the recipe's figures; the code below explains its library calls, and
the canonical driver at the end is what builds a product.

## Read the solar observation

The archived [configuration](../_static/tutorials/calibration-walkthrough/params_aug23_exact512.json)
specifies the source window, static window, antenna membership, and dated layout.
These lines show how the driver reads its full visibility triangle:

```python
import json
from pathlib import Path
from casm_io.correlator import AntennaMapping, load_format, read_visibilities

run_dir = Path("/mnt/nvme5/vishnu/cal_build_20260824")
params = json.loads((run_dir / "params_aug23_exact512.json").read_text())
fmt = load_format("layout_64ant")
mapping = AntennaMapping.load(params["layout_csv"])
ant = mapping.with_inactive(
    sorted(set(mapping.active_antennas()) - set(params["antennas"]))
)
data_raw = read_visibilities(
    *params["source_window"], time_tz="UTC", data_root="/mnt/nvme4/data/casm",
    fmt=fmt, verbose=False,
)
```

The selected window is **20:41:30–21:41:30 UTC on August 23**. The recorded
run contains 26 integrations. `vis` has axes **time, frequency, baseline**;
the calibration needs the full triangle, not just baselines to the reference.
This read can use several GB.

For a **new** observation, use the layout described in
[getting started](../getting-started.md); keep this example's dated layout
when replaying its historical data, and verify membership explicitly.

## Estimate and subtract the static background

This run averages a selected night window, **03:00–03:30 UTC on August 24**.
The driver uses `average_visibility` to build the template and saves it; we can
load that existing template to inspect the same processing step:

```python
from casm_vis_analysis.offsource import (
    load_static_visibility, subtract_static_visibility,
)

static = load_static_visibility(
    run_dir / "static_aug23_exact512_CAL0823N.npz"
)
data = subtract_static_visibility(data_raw, static["static_vis"])
```

The static represents persistent correlated background and instrumental pickup.
It is not an empty-sky measurement: Cyg A and Cas A were above the horizon in
this window. The source window and template must have compatible wiring,
frequency axes, and gain state. Keep the original data for power diagnostics.
Building a template for a new epoch is the
[static-template tutorial](static-template.md).

## Remove the Sun's geometric phase

```python
from casm_vis_analysis.fringe_stop import fringe_stop

fs = fringe_stop(
    data, ant, ref_ant=9, source="sun", sign=-1, min_alt_deg=10.0,
)
```

The antenna positions and Sun direction predict a geometric delay for each
baseline. Fringe stopping removes its time-dependent phase while preserving
instrumental phase. The saved notebook shows this using the existing RdBu plotter:

```{figure} ../_static/tutorials/calibration-walkthrough/fringe_diag_snap0_to_2.webp
:alt: Four reference-antenna baselines before and after Sun fringe stopping, with the geometric phase model between them.

Read one row from left to right: measured phase, predicted geometry, and
fringe-stopped phase. “Raw” here means before fringe stopping, after the run's
static subtraction. The more horizontal residual bands retain cable-delay phase.
```

Red and blue encode wrapped phase, not power or quality. A jump between them
can simply cross ±π. Check amplitude/coherence when the phase is noisy.

The same reference baselines show a familiar sawtooth when phase is averaged
over time and plotted against frequency:

```{figure} ../_static/tutorials/calibration-walkthrough/phase_raw_sawtooth_aug23_exact512_CAL0823N.webp
:alt: Wrapped phase versus frequency for nine short, medium, and long reference baselines in the same solar run.

Each wrap is a full phase turn. These are baseline phases before fringe stopping,
with both geometry and instrumental delay present. They are not yet per-antenna gains.
```

## Solve antenna gains with SVD

The canonical recipe passes the fringe-stop metadata and the static-subtracted
full triangle to `svd_calibrate`. Its fixed solver policy in this example is:

```python
from casm_calibrator import SVDConfig, SVDMode, svd_calibrate

config = SVDConfig(
    threshold=1.0, svd_mode=SVDMode.PHASE_ONLY,
    block_size=1, masked_band_strategy="zero",
)
cal = svd_calibrate(fs, ant, data=data, config=config)
```

For each frequency, the solver constructs an antenna-by-antenna matrix,
removes source geometry before averaging, and estimates antenna gain phases.
The phase-only matrix has its autocorrelation diagonal removed.

The reference antenna reaches the solve through `fs["ref_ant"]`, set by
`fringe_stop`. `svd_calibrate` reads it and overwrites `SVDConfig.ref_ant_idx`
with the reference's position in the active list, so setting `ref_ant_idx` on
the config has no effect. Antenna 9 is the reference here because
`fringe_stop(..., ref_ant=9)` was called above.

`SVDMode.PHASE_ONLY` forces unit-amplitude gains, and the production choice is
uniform amplitude for every antenna. The binary-mask incoherent beam requires
equal per-antenna `|w|` for CB-IB subtraction, which an inverse-variance
amplitude scheme breaks. Do not reintroduce amplitude weighting while
subtraction is in use.

```{figure} ../_static/tutorials/calibration-walkthrough/rank1_vs_freq_aug23_exact512_CAL0823N.webp
:alt: Rank-1 ratio versus frequency for this run, comparing static subtraction with no subtraction.

The ratio is the leading singular value divided by the second. Green and red
compare the same source window with and without the static template. Static
subtraction changes the matrix fit; a higher ratio alone does not prove a better beam.
```

The threshold above documents this recipe, not a universal readiness threshold.
The channel flags and the frequency-dependent structure matter alongside the
median. The Sun's changing structure also affects this diagnostic. Solving one
yourself and reading the singular spectrum is the
[rank-1 tutorial](rank1-diagnostics.md).

## Inspect gains and calibration weights

```python
print(cal["gains"].shape)       # (antenna, frequency)
print(cal["ant_ids"])          # identifies the antenna rows
print(cal["weights"].shape)     # same shape; conjugate of the gains
```

```{figure} ../_static/tutorials/calibration-walkthrough/gain_delay_fits_aug23_exact512_CAL0823N.webp
:alt: Per-antenna gain phase sawtooths and fitted delays for all sixteen antennas, referenced to antenna nine.

Blue is the solved gain phase; red is a fitted delay. Antenna 9 is flat because
it defines the reference. The correction weight has the opposite phase:
`weight = conjugate(gain)`.
```

A delay produces a frequency-dependent phase ramp, which wraps into a sawtooth.
Residual structure around the fitted delay deserves investigation. These are
instrumental corrections; they do not yet tell the array where to point.

## Add pointing geometry and make 512 beams

The driver selects an exact-response beam grid using the active antenna positions:

```python
from bf_weights_generator import Array64Config, FrequencyConfig
from bf_weights_generator import generate_beam_grid_exact

arr = Array64Config.from_antenna_mapping(ant)
freq_config = FrequencyConfig.layout_64ant()
pointings = generate_beam_grid_exact(
    arr.active_positions, freq_config.get_frequencies_hz(),
    n_beams=512, alt_min_deg=20.0, criterion="rate", floor_weight=0.0,
)
```

This is the geometric stage inside the existing driver, not a second product
builder. For each pointing, `generate_combined_weights` multiplies the stored
calibration correction by its geometric steering phasor, then maps antennas to
hardware slots. The driver converts and saves the int8 product with its metadata.
Grid placement takes about 15 s for 512 beams; the visibility reads dominate
the rest of the build.

Two hard constraints on this stage:

- **Exactly 512 beams.** The beamformer takes 512, not "about 512".
  `generate_beam_grid_exact` is greedy max-coverage: it scores a dense alt-az
  candidate lattice against the exact array-factor response on a
  solid-angle-weighted sky grid and adds the candidate that most improves
  coverage, one at a time, until `n_beams` pointings exist. There is no spacing
  search and no trim step.
- **`freq_order="descending"`.** That is the correlator's native channel order
  and what the driver passes. An ascending file flips the payload against the
  channel order the beamformer reads.

**Layout gating trap.** The weights stage intersects the requested antenna list
with the layout CSV's `include_in_beamforming` column: both that flag and
`functional` must be 1 for a slot to be active. An antenna present in the
calibration but flagged 0 in the layout silently drops out, and a near-empty
weights file still passes the driver's own verification, which samples one
channel's payload. Count the populated slots in the saved file before doing
anything with it:

```bash
casm-bf-inspect /mnt/nvme5/vishnu/cal_build_20260824/weights_aug23_exact512_CAL0823N_16ant_512_int8.h5
```

The last two lines print SNAP inputs with non-zero weights and active antennas
in the layout, both out of 64. They must equal the antenna count you asked for.

```{figure} ../_static/tutorials/calibration-walkthrough/beam_grid_aug23_exact512_CAL0823N.webp
:alt: The saved exact 512-beam pointing grid in azimuth and altitude, coloured by beam index.

Each dot is one saved beam pointing. This historical run requested coverage above
20°; its selected beam centres span 22° to 90°. Stars mark source-transit positions.
```

Pointing direction is separate from sensitivity: a grid location alone does not
prove that the corresponding live beam has correct gains or data.

## Overlay source tracks

The notebook uses the saved weights file to locate the actual grid:

```python
from bf_weights_generator.plot_transit import plot_source_transit

plot_source_transit(
    run_dir / "weights_aug23_exact512_CAL0823N_16ant_512_int8.h5",
    ["sun", "cyg-a", "cas-a", "b0329+54"],
    date="2026-08-25", time_tz="America/Los_Angeles",
)
```

```{figure} ../_static/tutorials/calibration-walkthrough/source_transit_aug23_exact512_CAL0823N.webp
:alt: Sun, Cyg A, Cas A and B0329 tracks over the saved beam grid, with altitude versus local time.

Left: source tracks and the grid's predicted response. Right: source altitude
through the selected day. These are geometric predictions, not measured source flux.
```

For precise transit timing use the existing exact array-factor report,
`casm-bf-source-transit --exact`. Do not infer timing or guaranteed sensitivity
from an approximate footprint or an altitude-coverage shaded region.

## Build the IB companion

The driver builds the coherent-beam file only. The incoherent beam is a
separate file, a binary mask over the 132-slot `snap*12+adc` vector with no
beam dimension, derived from the CB file so the two share the antenna set and
frequency grid. It is generated by a script outside the packages:

```bash
python /home/casm/scratch/bf_experiment_v1/scripts/gen_ib_from_cb.py \
  /mnt/nvme5/vishnu/cal_build_20260824/weights_aug23_exact512_CAL0823N_16ant_512_int8.h5 \
  /mnt/nvme5/vishnu/cal_build_20260824/ib_aug23_exact512_CAL0823N.h5 \
  8
```

Arguments are positional: CB file, output IB file, `bf_scale_factor`. Pass the
live `bf_scale_factor` from the wiki ledger; it is metadata only. The third
argument is stamped into `attrs["bf_scale_factor"]` (script L43, L65) and
nothing else: every mask value is 1 regardless of it. The live value has been 8
since 2026-09-02, so the script's built-in default of 64 and the `SCALE_IB=8`
text in its docstring are both stale. The script prints the
active CB slots it found, which must match the CB's populated slot count.
Deploying a CB without its matching IB leaves antennas out of the incoherent
sum and breaks the CB-IB subtraction condition.

## Check transfer before deployment

Review [cross-day baseline residuals](cross-day-phase.md) and a **stationary
Cyg A transit** using the [calibration-check tutorial](check-calibration.md).
The archived notebook also contains a tracking Cyg A coherence diagnostic; it
is useful additional evidence, but it is not the stationary transit-shape test.
Compare a control direction and keep source geometry, channel masks, and
antenna membership matched.

This build's own beam check, from `/beam_check/summary` in the
[saved report](../_static/tutorials/calibration-walkthrough/report_aug23_exact512_CAL0823N.json):

| Direction | Coherence |
|---|---|
| New cal | 0.0646 ± 0.0022 |
| Previous cal | 0.0674 ± 0.0021 |
| Null, 25° off | 0.0175 |

The new calibration scored below the previous one, by a difference comparable
to the quoted errors (ratio 0.957). Both sit well above the null, so both
work. This evidence does not favour replacing the deployed calibration, and
the product was not deployed.

Inspect the actual populated hardware slots, all requested diagnostics, and the
report itself. A missing or **SKIPPED** diagnostic is not a passed check.
Review CB and IB membership together.

## Run the canonical build when ready

The snippets above explain what already produced the example. For an approved
replay, keep the archived configuration intact and override its output directory.
The following creates a unique directory and only previews the settings:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
cd /home/casm
cal_example_dir=$(mktemp -d /tmp/casm-calibration-example.XXXXXX)
python -m bf_weights_generator.make_cal_and_weights \
  --config /mnt/nvme5/vishnu/cal_build_20260824/params_aug23_exact512.json \
  --param out_dir "$cal_example_dir" --print-params
```

After checking inputs and resource needs, the same invocation without
`--print-params` performs the build; use `--print-params` to preview a
configuration without running it. For new data, first prepare a reviewed
configuration with the current layout, appropriate windows, and explicit
antenna membership.

Generating files does not deploy them. The separate [deployment guide](deploy-weights.md)
covers inspected staging, human-approved upload, registry verification, and the
additional persistent choice to **save restart defaults**.

[Notebook provenance, cell map, and implementation notes](../developer/calibration-walkthrough-notes.md).
