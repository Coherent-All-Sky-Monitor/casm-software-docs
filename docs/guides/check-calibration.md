# Check whether a calibration transfers

Two complementary checks help assess an existing calibration: compare baseline
phase across days, and synthesize a known-source beam from independent
visibilities. Neither requires changing SNAP settings or uploading weights.

This is an analysis guide, not a calibration-generation or deployment recipe.
Examples are illustrative and have not been run on telescope data for this
preview. Operational builds remain in the existing
`bf_weights_generator.make_cal_and_weights` driver.

## Prepare a comparable experiment

Record the calibration file and revision, layout valid at each observation,
active antenna IDs, reference antenna, time window and timezone, frequency
coordinates, RFI mask, and any static visibility subtraction. Include gaps,
integration length, and known synchronization or gain changes.

Match source geometry or remove it consistently before comparing phase.
Use an independent later window to test transfer; reusing the solve window
primarily tests consistency with the training data. Begin with a bounded window
and a few baselines so selection errors and memory use are visible.

Check the canonical wiki `weights-verification.md` before interpreting a product.
In particular, synchronization/reflash events invalidate assumptions about a
standing coherent calibration, and gain changes can invalidate an older static
template's amplitudes. This guide authorizes no hardware action.

## 1. Compare the baseline sawtooth and residual

Use `casm_io` to load each day's visibility window and `AntennaMapping` to
resolve the same physical baseline, including any wiring changes. Fringe-stop
with the established `sign=-1` convention using
`casm_vis_analysis.fringe_stop.fringe_stop`.

Show both wrapped phase versus frequency (the sawtooth) and corrected residuals
on common good channels. For the visibility orientation
`V_ij = <v_i conjugate(v_j)>`, applying calibration correction weights gives
`V_corrected_ij = c_i conjugate(c_j) V_fringe_stopped_ij`.
Reverse-baseline selection requires conjugation; never use antenna IDs as flat
baseline-array indices.

The existing wiki validation battery names `plot_baseline_phase_validation` and
historical sawtooth scripts. Reuse the maintained routine appropriate to the
selected product; inspect its actual package/signature before invoking it.
For underlying plotting primitives, see [Visibility analysis](../packages/vis-analysis.md).

For every residual plot, report:

- The exact antenna pair and orientation, reference, dates, and selected samples.
- Raw and corrected phase on the same frequency mask.
- Circular phase scatter or another explicitly defined residual statistic.
- Coherence or amplitude support, because phase of near-zero signal is unreliable.
- Any frequency gaps, unwrapping choices, slope fit, and rejected samples.

Historical wiki examples use residuals near 0.3 radians as a useful benchmark.
That is evidence from particular baselines and epochs, not a universal threshold.
A small residual supports stability for the measured baseline and window; it
does not establish sensitivity or correct geometry in every direction.

## 2. Form a stationary Cyg A transit beam

Choose a window covering a Cyg A transit with off-transit samples. Apply the
candidate calibration to the visibilities, and synthesize a fixed beam at a
chosen point on that track. Compare its response with the expected synthesized
beam and a control pointing away from the source track.

The existing `beam_power_vs_time` supports fixed `(label, altitude, azimuth)`
pointings. A source-name string instead tracks the source; it will not measure
the same stationary-beam transit shape.

```python
from bf_weights_generator.snap_weights import load_calibration_weights
from casm_vis_analysis.beam_power import beam_power_vs_time, plot_beam_power

cal = load_calibration_weights("/path/to/candidate-calibration.h5")

# data and ant come from the bounded, independent Cyg A window.
# Set these angles from the selected source track and array-factor prediction.
pointings = [
    ("Cyg A fixed beam", target_alt_deg, target_az_deg),
    ("Off-source control", control_alt_deg, control_az_deg),
]
result = beam_power_vs_time(
    data, ant, sources=pointings,
    cal_weights=cal,
    freq_band_mhz=analysis_band_mhz,
    sign=-1,
)
figure = plot_beam_power(result, time_tz="America/Los_Angeles")
```

Angles, band, and data variables above are intentional placeholders requiring
scientific selection. The output is a frequency-averaged cross-baseline power
series. It excludes autos and is not flux calibrated. Frequency alignment is
checked by the library; do not suppress a mismatch or reverse only one array.

Compare calibrations using identical evaluation data, antenna membership,
weights normalization, masks, and controls. If you subtract a static template,
label that metric separately from the raw-data result. A template recorded
before an instrumental amplitude change is not interchangeable with a matched
template recorded afterwards.

## 3. Check the beam grid separately

`validate_source` and `plot_source_validation` compare a source track with
pointings embedded in an int8 product and synthesize corresponding visibility
responses. They are useful grid diagnostics, but their geometric hit regions
use FWHM approximations. The wiki records inaccurate transit-peak estimates
from such approximations; use the existing exact array-factor transit prediction
in `bf_weights_generator` when timing or detailed shape matters.

A built file's metadata does not prove which payload is serving on the nodes.
That is a distinct operational verification described in wiki
`weights-verification.md`; it is not established by this offline check.

## Report what the experiment establishes

| Finding | Supported interpretation |
|---|---|
| Stable residual on matched baselines | Phase transfer works on those baselines/windows |
| Correct stationary source response | Calibration plus geometry supports that direction |
| Improved solve rank-1 ratio alone | Matrix fit changed; beam improvement remains unproven |
| No source response and incomplete coverage | Inconclusive; first resolve data coverage |
| Different solar intensity between days | Could be intrinsic solar variability |

The wiki's `rank1-metric-caveat.md` documents cases where higher rank-1 solved
the Sun more cleanly but beamformed another source worse. It also records
direction-dependent calibration rankings when an antenna position was wrong.
A Cyg A check therefore does not certify the whole sky or FRB recovery.

Keep the result as a reproducible investigation: inputs, configuration, plots,
statistics, interpretation, limitations, and next discriminating check. Any
recommendation to rebuild or upload weights should link that evidence and
return to the canonical workflow with human authorization.

## Provenance

Reviewed on 2026-09-13 against `casm_vis_analysis` revision `5039eb4714b5`,
`casm_calibrator` revision `8b5fcf5b089d`, and the local wiki's `recipes.md`,
`weights-verification.md`, `rank1-metric-caveat.md`, and `software-map.md`.
The wiki remains the canonical location for dated operational findings.
