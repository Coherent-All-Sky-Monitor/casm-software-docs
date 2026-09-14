# SVD Calibration Reference

## Overview

`svd_calibrate` takes a fringe-stopped result from `casm_vis_analysis` and
the full-triangle visibilities from `casm_io`, builds a per-channel Hermitian
visibility matrix, and extracts per-antenna complex gains via rank-1 SVD.

The central assumption is that the time-averaged, fringe-stopped visibility
matrix is approximately rank-1: V_ij = g_i * g_j*. The ratio sigma_1/sigma_2
(the two largest singular values) measures how well the data satisfies this
assumption per channel.

## Primary function

```python
svd_calibrate(fs, ant, *, data, config=None, time_mask=None) -> CalibrationResult
```

| Parameter | Type | Notes |
|-----------|------|-------|
| `fs` | dict (FringeStoppedData) | Output of `casm_vis_analysis.run_fringe_stop`. Provides `freq_mhz`, `time_unix`, `ref_ant`, `source`, `time_mask`, `freq_mask`. |
| `ant` | `AntennaMapping` | Active antenna set; respects `with_inactive` overrides. |
| `data` | VisibilityResult or dict-like | **Keyword-only, required.** Full-triangle visibilities from `casm_io.read_visibilities`. The `vis` key must be `(T, F, n_bl)` complex64. |
| `config` | `SVDConfig` or None | Defaults to `SVDConfig()` (threshold=4.0, PHASE_ONLY, per-channel). |
| `time_mask` | bool ndarray, shape (T,) or None | Restricts time average. Defaults to `fs['time_mask']` if present. |

`data` is keyword-only because the full-triangle array (N*(N+1)/2 baselines)
is structurally different from the ref+target subset carried on `fs`. Accepting
it positionally would make it easy to pass the wrong thing silently.

### Input validation and masks

`data` must provide `vis`, `freq_mhz`, and `time_unix` (mapping keys or
attributes). The visibility cube must have nonempty `(T, F, B)` dimensions,
with `B = n_inputs*(n_inputs+1)/2`. Both frequency axes must be finite `(F,)`
arrays and match exactly in value and order. Time coordinates must be finite
`(T,)` arrays; when `fs['time_unix']` is present it must match the data exactly.
When it is absent, data timestamps are used. The wrapper preserves the supplied
frequency order, including descending order; it does not sort or resample.

At least two active antennas are required, with unique integer packet indices
inside the visibility input range. Selected visibility samples, antenna
positions used for fringe stopping, and source directions must be finite.
The low-level solver also rejects empty, nonsquare, nonfinite, or single-antenna
matrices and reference indices outside the matrix before SVD.

Reader baseline metadata is checked before matrix construction. `inputs` must
be a sorted, unique list of native packet indices describing the stored
subtriangle; every active antenna must be present. Calibration remaps packet
indices to subtriangle ranks and retains antenna IDs in the output. It checks
`nsig` and `nsig_subset` against the cube, and rejects ref/targets-only data even
when its baseline count happens to be triangular. Conflicting top-level and
nested metadata raises `ValueError`. Without selection metadata, the historical
full native triangle contract applies.

This subset support is specific to `svd_calibrate(data=...)` and the matrix
helper. The upstream `casm_vis_analysis.fringe_stop` wrapper rejects input
subsets; normal composed workflows should read the full native triangle.

`time_mask` must be `(T,)`, with at least one True sample. An explicit mask
overrides `fs['time_mask']`, but cannot enable unavailable integrations.
`valid_integrations` from data's top level, reader metadata, and `fs` are
intersected with the selected time mask. Missing availability preserves legacy
behavior; False and unknown (`None`) rows are excluded. Availability accepts
booleans or numeric 0/1, rejects malformed values/shapes, and an empty available
selection raises `ValueError` before matrix construction. Thus zero-filled
missing file rows cannot masquerade as a valid phase-only solve.

`freq_mask` must be `(F,)`; malformed masks raise
`ValueError` before matrix construction in both per-channel and subband modes.
Boolean conversion remains supported, and True means include/good. All-False
frequency masks remain supported. The existing `zero`, `geo_fallback`, and
`extrapolate` policies are unchanged, including their behavior when every
subband fails. Samples excluded by the time mask do not enter the finite
visibility check or time average.

In subband mode, frequency-masked channels also do not enter the finite check
or average. NaNs restricted to these excluded channels are permitted, and the
chosen masked-band output strategy still applies. The direct subband helper
follows the same rule. The legacy per-channel/block solver still processes
every channel before applying its output mask, so it requires finite data
throughout the selected time samples.

### Helper replacement compatibility

The historical root imports `_build_hermitian_matrix`, `_build_baseline_mask`,
and `_subband_svd_with_smooth_fit` remain callable. Replacing any of them at
`casm_calibrator.<name>` intercepts `svd_calibrate` again. Root replacements
take precedence over bindings in `casm_calibrator.calibration`; otherwise the
orchestration module's bindings are used. Replacements should accept the new
optional matrix keywords `input_indices` and `freq_mask` when those selections
are requested. Patching arbitrary implementation internals is not a public API.

### Why fringe-stop before time-averaging

`svd_calibrate` builds the Hermitian matrix by fringe-stopping each baseline
toward `fs['source']` before time-averaging. Without this, the rotating
geometric phase washes out the source signal across the integration window and
sigma_1/sigma_2 collapses. This happens inside `_build_hermitian_matrix` and
is automatic when `fs['source']` is set.

### Reference antenna remapping

`svd_calibrate` maps `fs['ref_ant']` (an antenna ID) onto the 0-indexed
position in `sorted(ant.active_antennas())` and injects that as `ref_ant_idx`
in a copy of the config; the caller's config is unchanged. An inactive or
unknown reference raises `ValueError` before matrix construction, so the
recorded `ref_ant_id` always identifies the actual solve reference.
Do not set `ref_ant_idx` manually in `SVDConfig` when calling
`svd_calibrate`; it will be overwritten. Set it only when calling
`SVDCalibrator.calibrate` directly on an externally-built matrix.

## SVDConfig

```python
from casm_calibrator import SVDConfig, SVDMode

cfg = SVDConfig(
    threshold=5.0,                       # recommended for strong cal sources
    svd_mode=SVDMode.PHASE_ONLY,         # recommended; most robust
    ref_ant_idx=0,                       # overwritten by svd_calibrate; set only for direct SVDCalibrator use
    block_size=1,                        # 1 = per-channel SVD (default)
    fill_mode="interpolate",             # failed-block fill strategy
    subband_size=None,                   # None = per-channel path (default)
    subband_min_good_frac=0.5,
    smooth_order=3,
    fill_failed="smooth_fit",
    masked_band_strategy="zero",         # recommended
    min_baseline_wavelengths=None,
    amp_weighting="none",
)
```

`svd_mode` accepts either an `SVDMode` enum member or its string value
(e.g. `"phase-only"`). `__post_init__` coerces strings automatically. Unknown
strings raise `TypeError`, not `ValueError`.

### Field reference

#### `threshold`

Minimum sigma_1/sigma_2 ratio for a channel or subband to be flagged good.

| Value | Use case |
|-------|----------|
| `5.0` | **Recommended** for production Sun calibration. Yields ~753 good channels of 3072 in typical daytime observations. |
| `3.0`-`4.0` | Weaker sources (Cas A, Cyg A) or shorter integrations. |
| `2.0` | Legacy compatibility with pre-`casm_calibrator` pipelines (correlator_analysis default). Passes more channels but accepts noisier solutions. |

Lower thresholds pass more channels at the cost of noisier gains. Check
`int(np.sum(cal['flags']))` before deploying any calibration file.

#### `svd_mode`

How to prepare the per-channel visibility matrix before SVD.

| Mode | Enum | String | Input matrix | Gain extraction |
|------|------|--------|-------------|-----------------|
| **Phase-only** | `SVDMode.PHASE_ONLY` | `"phase-only"` | `exp(1j * angle(V))` — all baselines normalized to unit amplitude | `exp(1j * angle(U[:,0]))` |
| Complex | `SVDMode.COMPLEX` | `"complex"` | Raw V (amplitude kept) | `U[:,0] * sqrt(sigma_0)`, phase-referenced |
| Cross-only | `SVDMode.CROSS_ONLY` | `"cross-only"` | Raw V, diagonal zeroed | Same as COMPLEX |
| Raw | `SVDMode.RAW` | `"raw"` | Raw V including diagonal | Same as CROSS_ONLY |

The autocorrelation diagonal is always zeroed before SVD regardless of mode.
It carries no phase information and leaving it in `PHASE_ONLY` mode would add
a spurious all-ones rank-1 component.

**Recommended: `PHASE_ONLY`.** Normalizing to unit amplitude makes the SVD
insensitive to large auto-power variation (30x spread is typical across CASM
antennas). This maximizes the pass rate and gives the most consistent gain
solutions across observations.

**`COMPLEX`**: preserves per-antenna amplitude in the gains. Useful if you
want the absolute calibration (not just phases), but note that COMPLEX and RAW
currently use the same input matrix (amplitude-preserved raw V). The gain
extraction differs: COMPLEX scales by sqrt(sigma_0), CROSS_ONLY/RAW do not.
See the known gotcha below.

**`CROSS_ONLY`**: zeroes the diagonal before SVD. Similar to COMPLEX in
practice; the distinction matters for extended-emission-dominated channels.

**`RAW`**: keeps autocorrelations. Auto-power dominates and the rank-1 ratio
collapses on many channels. Lowest pass rate; use only for debugging.

Known gotcha: `COMPLEX` and `RAW` share the same `_prepare_svd_input` branch
(both take a raw complex copy of V). The gain extraction is correct for
`COMPLEX` but the conditioning of the input matrix is identical. Tracked as
SF-16. Do not rely on `COMPLEX` producing a differently-conditioned matrix.

#### `masked_band_strategy`

Controls what happens at channels the user-provided RFI mask marks bad. Channels in the RFI mask get
gains zeroed and flags set to False. This is the safe default: RFI is
typically 30-50 dB above thermal noise and a phase-only calibration cannot
reduce power, so passing the channel through any calibration loses more than
it gains.

| Strategy | Gains at masked channels | Flags | Use when |
|----------|--------------------------|-------|----------|
| `"zero"` | 0 (default, **recommended**) | False | Always safe |
| `"geo_fallback"` | 1+0j (unit cal) | True | Channel known clean at observation time but flagged at cal build time |
| `"extrapolate"` | Polynomial smooth-fit values | True | Low-cal-SNR but actually clean channels; requires subband path |

Note: `masked_band_strategy` is applied twice in the subband path (once inside
`_subband_svd_with_smooth_fit`, once in `svd_calibrate`). For `"zero"` and
`"geo_fallback"` this is idempotent. For `"extrapolate"`, it can flip `flags`
unexpectedly. Tracked as SF-2.

#### `block_size`

Number of channels averaged before SVD. `1` (default) gives per-channel
solutions. Values like `32` or `64` boost SNR on weaker sources at the cost
of frequency resolution. Failed blocks are filled by the `fill_mode` strategy.

#### Subband + smooth-fit path

Activated when `subband_size` is not None (integer). Instead of per-channel
SVD, this path:

1. Groups channels into subbands of `subband_size` channels.
2. Runs SVD on each subband mean (skipping RFI-flagged channels inside the mean).
3. Marks subbands failed if too few clean channels remain (`subband_min_good_frac`) or if sigma_1/sigma_2 < threshold.
4. Fits a per-antenna polynomial of order `smooth_order` across valid subband gains (phase unwrapped before fitting).
5. Evaluates the polynomial at every channel.

**Do not promote `smooth_order=1, subband_size=16` to production default.**
It improves image SNR by ~18% but degrades beam-transit SNR. See
`project_validation_final_state_2026_05_15.md`. The default (no smoothing) is
the safer choice until further testing.

If every subband fails, `_subband_svd_with_smooth_fit` returns all-zero gains
and all-False flags under the default `zero` strategy. `geo_fallback` still
sets masked channels to unit gains and True flags; `extrapolate` sets their
flags True even when no fit is available and gains remain zero. Always check
`int(np.sum(cal['flags']))` before writing or deploying a calibration file.

#### `min_baseline_wavelengths`

Excludes baselines shorter than N wavelengths (at the highest in-band
frequency) from the SVD input matrix. Set to `1.5` when calibrating on the Sun:
at 410 MHz, sub-1.5-lambda baselines see solar corona and Galactic background
structure that violates the rank-1 source assumption and contaminates
sigma_2. Default `None` preserves current behavior (no cut).

## CalibrationResult

`svd_calibrate` returns a `TypedDict` with the following fields:

| Key | Shape | dtype | Description |
|-----|-------|-------|-------------|
| `gains` | `(n_ant, n_chan)` | complex128 | Per-antenna complex gains |
| `weights` | `(n_ant, n_chan)` | complex128 | `conj(gains)` |
| `flags` | `(n_chan,)` | bool | True = good channel |
| `rank1_ratios` | `(n_chan,)` | float64 | sigma_1/sigma_2 per channel |
| `singular_values` | `(n_chan, n_ant)` | float64 | Full singular value spectrum |
| `freqs_mhz` | `(n_chan,)` | float64 | Channel frequencies |
| `ant_ids` | `(n_ant,)` | int | Active antenna IDs |
| `ref_ant_id` | scalar | int | Reference antenna ID (phase = 0) |
| `source` | — | str | Calibrator source name |
| `layout_version` | — | dict | Antenna layout provenance (when available) |

`CalibrationResult` is defined in `results.py` and re-exported from the package.
Both its schema and the returned gains use `(n_ant, n_chan)`.

## Low-level engine

For one-shot SVD on an externally-built `(F, N, N)` Hermitian matrix:

```python
from casm_calibrator import SVDCalibrator, SVDConfig, SVDMode

result = SVDCalibrator(
    SVDConfig(threshold=5.0, svd_mode=SVDMode.PHASE_ONLY)
).calibrate(vis_avg)
# result: SVDResult dataclass with gains, weights, flags, rank1_ratios, singular_values
```

`SVDResult` is a dataclass (not a TypedDict). Its `gains` are `(n_ant, n_chan)`.
`ref_ant_idx` in the config is respected directly here (no remapping).

## Diagnostic plots

```python
from casm_calibrator import plot_calibration

figs = plot_calibration(
    cal,
    threshold=5.0,
    rfi_ranges=[(375, 390), (450, 452)],
    output_path="cal_diagnostics.png",   # None = plt.show()
    ant=ant,                              # optional; enables richer labels
)
# figs: list of 3 Figure objects (rank1, phase, amplitude)
```

When `output_path` is given, saves three PNGs:
`{base}_rank1.png`, `{base}_phase.png`, `{base}_amp.png`.
When `output_path` is None, calls `plt.show()`.
