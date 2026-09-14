# Cross-day calibration checks

Advanced examples for comparing baseline phases between observing days. Begin
with the [Cyg A transit tutorial](../guides/check-calibration.md) for the visual introduction.

Two complementary checks help assess an existing calibration: compare baseline
phase across days, and synthesize a known-source beam from independent
visibilities. Operational builds stay in
`bf_weights_generator.make_cal_and_weights`.

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
template's amplitudes.

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

`plot_baseline_phase_validation` is cell 28 of
`casm_vis_analysis/notebooks/casm_calibration_and_beamforming.ipynb`; the
package does not export it. It takes `(cal_h5, data_day, *, ref_ant,
target_ant, rank1_thresh, window, fringe_stopped)` and compares `angle(V)` on
the reference-to-target baseline with `angle(g_ref * conj(g_tar))` from the
cal file. The packaged primitive underneath is
`casm_vis_analysis.plotting.phase_freq.plot_phase_vs_freq`; see
[Visibility analysis](../packages/vis-analysis.md).

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

The [Cyg A tutorial](../guides/check-calibration.md) runs this end to end on
real data: exact array-factor prediction, full-triangle read, static
subtraction, `load_calibration_weights`, `beam_power_vs_time` with a fixed
pointing and an altitude-offset control, and the half-max midpoint and on/off
numbers. Use it rather than a second copy of the same call here.

Points that matter when comparing candidates:

- Identical evaluation data, antenna membership, weights normalization, masks
  and control for every cal, or the comparison means nothing.
- Label the static-subtracted metric separately from the raw one. The two
  disagreed by a factor of nine on 2026-08-20 (66% versus 7% of the self-cal
  ceiling).
- A static template recorded before an instrumental amplitude change does not
  transfer across it.
- A source-name string in `sources` tracks the source and gives a flat
  coherence level, not a transit shape. Use the `(label, alt, az)` tuple.
- The output is frequency-averaged cross-baseline power, autos excluded, not
  flux calibrated. The library checks frequency alignment; do not suppress a
  mismatch or reverse only one array.

## 3. Check the beam grid separately

`validate_source` and `plot_source_validation` compare a source track with
pointings embedded in an int8 product and synthesize corresponding visibility
responses. They are useful grid diagnostics, but their geometric hit regions
use FWHM approximations. The wiki records inaccurate transit-peak estimates
from such approximations; use the existing exact array-factor transit prediction
in `bf_weights_generator` when timing or detailed shape matters.

A built file's metadata does not prove which payload is serving on the nodes.
The as-deployed subband decode in wiki `weights-verification.md` (check b) is
the only thing that does.

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

