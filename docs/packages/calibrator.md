# Calibration

`casm_calibrator` estimates antenna gains from a source-fringe-stopped
visibility matrix and provides calibration products consumed by
`bf_weights_generator`. It is the calibration engine, not the telescope
deployment interface.

This page includes the September 13 [audit candidate](../developer/audit-release.md);
the [source snapshot](../sources.md) identifies its inspected revision.
Examples are illustrative, signature-checked snippets, not validated observing
recipes. Bounded regression solves do not establish an observing recipe.

## Start with the right workflow

For an operational calibration-and-weights build, use the existing
`bf_weights_generator.make_cal_and_weights` driver and its
`docs/canonical-recipe.md`. It already coordinates solve, beam grid, int8
products, verification, and diagnostic outputs. Do not replace that workflow
with an ad hoc sequence assembled from this API page.

Use this package directly when understanding that driver, inspecting a saved
calibration, or developing a controlled offline analysis. See the
[calibration-check guide](../guides/check-calibration.md) before interpreting
quality metrics and the [API inventory](calibrator-api.md) for signatures.

## Installation

Use `casm_offline_env`, the default environment for Vishnu's repositories:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
python -c "import casm_calibrator; print(casm_calibrator.__file__)"
```

Use existing installs first. For a newly prepared environment, upstream
supports `python -m pip install -e '/path/to/casm_calibrator[dev]'` after
installing `casm_io` and `casm_vis_analysis`.
Production configuration, RFI ranges, active antennas, and observing windows
come from the approved driver configuration, not defaults copied from examples.

## Data flow and public API

| Interface | Role |
|---|---|
| `svd_calibrate(fs, ant, *, data, config, time_mask)` | Construct source-fringe-stopped Hermitian matrices and solve gains |
| `SVDConfig`, `SVDMode` | Explicit solver configuration |
| `plot_calibration(cal, ...)` | Rank-1 ratio, gain phase, and amplitude plots |
| `save_calibration(cal, path, ...)` | Write HDF5 or legacy NPZ calibration |
| `SVDCalibrator` | Lower-level matrix solver |

The keyword-only `data=` argument is required. It contains the original full
upper triangle; the reference-to-target subset in `fs` is insufficient to
construct the full antenna matrix. The function removes geometric phase on
each baseline before averaging the selected times.

The candidate validates the reference antenna's membership and requires matching
frequency and time axes between `fs` and `data`, including their order. Masks
must have the exact axis length; malformed masks raise `ValueError` rather than
being ignored. Solver masks use `True = include`. Nonfinite selected data are
rejected. These checks run before the solve and do not establish scientific
suitability of a valid-shaped input.

Reader input identities are validated before matrix indexing. The lower-level
calibrator can remap a labeled subtriangle only when it contains every active
antenna; `fringe_stop` still requires a supported full-triangle input. Missing
rows and zero-signal selections cannot produce a successful solve. In subband
mode, nonfinite values confined to excluded frequency channels do not invalidate
the included channels; this exception does not apply to per-channel mode.

The package root retains public imports. Matrix preparation, input validation,
subband solving, and product persistence now live in separate implementation
modules listed in the refreshed API reference.

The following shows the solver interface, assuming `fs`, `ant`, and `data`
were prepared by the existing pipeline:

```python
from casm_calibrator import SVDConfig, SVDMode, svd_calibrate

config = SVDConfig(
    svd_mode=SVDMode.PHASE_ONLY,
    masked_band_strategy="zero",
)
cal = svd_calibrate(fs, ant, data=data, config=config)
print(cal["weights"].shape)
print(cal["freqs_mhz"][[0, -1]])
print(cal["ant_ids"], cal["ref_ant_id"])
print(int(cal["flags"].sum()), len(cal["flags"]))
```

This uses library defaults for omitted solver fields to illustrate the call;
it does not recommend those values for a deployment. Explicit `time_mask=`
overrides `fs['time_mask']`; otherwise the function inherits that selection.
Reader availability still limits that mask: missing integrations cannot be
re-enabled by an explicit selection, and an empty available selection raises.

## Interpret a calibration result

| Field | Meaning |
|---|---|
| `weights` | Complex correction weights, `(antenna, channel)` |
| `gains` | Estimated complex gains, same shape |
| `flags` | Per-channel boolean usability mask; `True` means good |
| `freqs_mhz` | Frequency coordinate in MHz; inspect its actual order |
| `ant_ids` | Antenna IDs corresponding to rows |
| `ref_ant_id` | Phase reference antenna ID, not matrix-row index |
| `rank1_ratios` | Per-channel solver-quality diagnostic |
| `source` | Calibrator source label |

The array convention is `V[i,j] = <v_i conjugate(v_j)>`. Runtime beamforming
applies a weighted voltage sum without conjugating the supplied weight.
Consequently calibration weights are the conjugate of estimated gains.
An old opposite-conjugation interpretation was explicitly retracted upstream.

`phase-only`, `cross-only`, and `raw` change the visibility matrix presented
to SVD. Block averaging and subband smooth fitting change the estimator further;
their metrics are not automatically comparable. Record all configuration fields.

`masked_band_strategy="zero"` keeps RFI-masked channels excluded. Other strategies
can mark extrapolated or geometric-only channels usable. Thus a count of
`flags=True` is not always a count of independently measured calibration gains.

## Inspect and save existing products

The downstream loader lives in `bf_weights_generator`:

```python
from bf_weights_generator.snap_weights import load_calibration_weights

saved = load_calibration_weights("/path/to/calibration.h5")
print(saved.weights.shape)
print(saved.frequencies_hz[[0, -1]])
print(saved.ant_ids)
```

`save_calibration` writes HDF5 for `.h5`/`.hdf5`, or NPZ for `.npz`.
It creates parent directories and refuses an existing file unless
`overwrite=True`. An additional `rfi_mask` is ANDed with the result's flags;
excluded weights and gains are zeroed in the output. Weights are stored as
`complex64`. Integration count is recorded only as supplied by the caller.

A calibration HDF5 is not a hardware int8 beam-weights file. The latter belongs
to `bf_weights_generator` and includes beam geometry and hardware slot ordering.
The legacy `CalibrationWeightsWriter` takes an `SVDResult` and writes NPZ;
new composed code should use `save_calibration`.

## Known documentation discrepancies

Older `CLAUDE.md` says internal processing and saved frequencies are always
ascending. At this revision, `svd_calibrate` carries `fs['freq_mhz']` into its
result and `save_calibration` preserves that order. Do not reverse arrays based
on that old prose: compare actual frequency coordinates and antenna IDs.

The same historical document describes 16 active antennas and a mandatory
daily solve. Neither is a timeless package contract. Current deployment
membership and whether calibration has aged require dated operational evidence.
Library threshold defaults and historical recommended thresholds differ too;
neither establishes astronomical performance on its own.

A higher rank-1 ratio measures a better matrix fit, not necessarily a better
beam. Validate independent source windows and record static-subtraction choices,
frequency masks, geometry, and antenna membership.

## Upstream reading

- [README](https://github.com/Coherent-All-Sky-Monitor/casm_calibrator/blob/8b5fcf5b089d6725e3c2c6b22d72c076e7ae74b3/README.md)
- [SVD configuration](https://github.com/Coherent-All-Sky-Monitor/casm_calibrator/blob/8b5fcf5b089d6725e3c2c6b22d72c076e7ae74b3/docs/svd_calibration.md)
- [Calibration I/O](https://github.com/Coherent-All-Sky-Monitor/casm_calibrator/blob/8b5fcf5b089d6725e3c2c6b22d72c076e7ae74b3/docs/calibration_io.md)
