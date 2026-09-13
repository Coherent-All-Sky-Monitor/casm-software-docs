# Read SVD and rank-1 diagnostics

Rank-1 diagnostics describe the visibility matrix used in a calibration solve.
They help locate unusual channels and compare controlled solve variants.
They do not measure beam sensitivity or FRB recovery.

This tutorial uses the existing calibrator and recipe diagnostic functions.
The examples operate on saved products or an already available in-memory result;
they do not generate or deploy new calibration weights.

## What the numbers mean

At each frequency, SVD decomposes the prepared antenna-by-antenna matrix.
Write its ordered singular values as `sigma_1 >= sigma_2 >= ...`.

| Diagnostic | Definition | Use |
|---|---|---|
| Rank-1 ratio | `sigma_1 / sigma_2` | Dominance of the leading component |
| Rank-1 fraction | `sigma_1 / sum(sigma)` | Leading share of the singular-value sum |
| Channel flag | Solver acceptance plus mask/fill policy | Which output channels are treated as usable |

The current phase-only solver replaces entries by their phases and zeros the
autocorrelation diagonal. For an ideal coherent point source with `N > 2`
participating antennas, no excluded cross-baselines, and consistent phases, this
prepared matrix has singular values `N-1, 1, ..., 1`. The ideal ratio is `N-1`
and its rank-1 fraction is **0.5**. A fraction below 1 is therefore expected.
With two antennas the zero-diagonal ratio cannot discriminate coherence.

This ceiling depends on matrix preparation. Short-baseline exclusions, amplitude
weighting, other modes, missing information, and block/subband averaging change
the experiment. Normalize comparisons by explicit membership and configuration;
do not compare raw ratios across different array sizes as an efficiency metric.

## 1. Inspect the existing build outputs

```{figure} ../_static/tutorials/calibration/rank1_vs_freq_20260820.png
:alt: Solar solve rank-1 ratio against frequency, with and without night-static subtraction.

Archived 16-antenna solar solve, 2026-08-19 20:41:30–21:41:30 UTC. Static
subtraction raises the ratio across much of the band. That change alone does
not demonstrate better beamforming. [Figure provenance](calibration-figures.md).
```

```{figure} ../_static/tutorials/calibration/svd_vs_freq_20260820.png
:alt: Singular values and leading singular-value fraction for the same solar solve.

The same solve's leading singular value approaches 15 and its fraction approaches
0.5 in the highlighted historical analysis band. The legend's `1/N` line is a
mathematical lower bound on the fraction, not a measured random-phase noise level.
The highlighted band is not a default RFI mask. [Provenance](calibration-figures.md).
```

The [canonical build](generate-weights.md) saves
`rank1_vs_freq_<tag>.npz`, `report_<tag>.json`, and diagnostic figures under
`figs/`. Start with the notebook, including its **SKIPPED** sections.

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
cd /home/casm
```

The NPZ is a documented derived diagnostic archive, not a raw correlator format:

```python
import numpy as np
import matplotlib.pyplot as plt

with np.load("/path/to/rank1_vs_freq_reviewed.npz", allow_pickle=False) as record:
    frequency = record["freq_mhz"]
    ratio = record["rank1"]
    antenna_ids = record["antennas"]

print(frequency.shape, ratio.shape, antenna_ids)
print("Frequency endpoints (MHz):", frequency[[0, -1]])
figure, axis = plt.subplots()
axis.plot(frequency, ratio, linewidth=0.7)
axis.set(xlabel="Frequency (MHz)", ylabel="sigma_1 / sigma_2")
axis.grid(alpha=0.25)
plt.show()
```

The arrays share their stored frequency order; do not reverse one alone.
Inspect nonfinite values explicitly. In the per-channel implementation,
`sigma_2 == 0` produces an infinite ratio; that arithmetic branch alone is
not evidence of a useful signal. Check the singular values and input support.

## 2. Use the existing multi-panel diagnostic

When `cal` is the in-memory `CalibrationResult` already returned by the driver:

```python
from casm_calibrator import plot_calibration

# Match the threshold recorded for this solve, rather than a library default.
figures = plot_calibration(
    cal, threshold=solve_threshold, ant=ant, output_path=None,
)
```

This shows rank-1 ratios, per-antenna gain phases, and amplitudes. Supplying a
path instead saves three suffixed files and closes the figures.
Flags remove excluded channels from the phase/amplitude display; report their
fraction separately so gaps are not mistaken for good measurements.

For the singular spectrum and fraction, use the driver's existing renderer:

```python
from bf_weights_generator.recipe_diagnostics import plot_svd_vs_freq

path, statistics = plot_svd_vs_freq(
    cal,
    "/path/to/new-figures/svd_review.png",
    "Reviewed solve: source, UTC window, antenna membership",
)
print(statistics)
```

The destination directory must exist. This saves a figure, not a weights file.
`cal['singular_values']` is required. Standard `save_calibration` HDF5/NPZ output
does not persist the full singular spectrum, so the saved ratios alone cannot
reconstruct this plot. Retain the driver's existing figure/report or rerun only
through an authorized canonical analysis if that information is needed.

## 3. Investigate a change in a controlled order

1. Check coverage, source altitude, frequency configuration, and instrument events.
2. Match antenna membership, source-relative window, integration count, and masks.
3. Compare per-frequency structure before summarizing it with a median.
4. Inspect gain sawtooths and corrected baseline residuals for the same inputs.
5. Evaluate an independent source beam, with an off-source control.

A whole subband behaving differently warrants checking delivery and masking,
but the ratio alone does not identify the cause. Phase-only normalization
discards amplitude information; inspect input powers and coherent signal too.

Static subtraction can improve the ratio by changing the matrix's secondary
components while leaving transferred phases almost unchanged. Solar variability
and changing window placement also affect the solve. The wiki's
`rank1-metric-caveat.md` records examples where a higher ratio accompanied worse
pulsar beamforming, and where calibration rankings depended on direction.

Use the [phase and Cyg A guide](check-calibration.md) to test transfer. Keep
injection recovery as a separate search-path measurement.

## Current source versus older prose

At calibrator revision `8b5fcf5b089d`, `_prepare_svd_input` zeros the diagonal in
**all** modes, including `raw`. Older descriptions that raw mode retains autos
do not describe this implementation. `complex` mode also exists and differs
in gain extraction. Default library thresholds are not the driver's fixed policy.

Reviewed 2026-09-13: `svd.py` SHA256
`d3a9dff69b139be45da78577a3de457293d1bfb29c808ef63af2011298bdcf0f`;
`recipe_diagnostics.py` at `bf_weights_generator` revision `06004c75afad`, SHA256
`9ab94c4f545efc413383a3ce48db8c7aba17625946fc0fb3d13cad0b728dcdfc`.
The calibrator checkout contains unrelated untracked experimental files;
this tutorial uses the tracked SVD implementation, not those experiments.
