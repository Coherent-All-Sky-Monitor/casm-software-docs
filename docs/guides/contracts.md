# Data contracts

These contracts are relevant to the inspected software. Always read the
metadata for the selected observation; historical data may use another format.

## Axes and units

| Quantity | Common representation | Check |
|---|---|---|
| Visibility array | `(time, frequency, baseline)` complex | Baseline subset and ordering |
| Frequency | MHz in the visibility interface | Read returned endpoints; do not assume ascending order |
| Time | Unix seconds in visibility results | Gaps, integration cadence and timestamp convention |
| Antenna position | East, north, up in metres | Layout epoch and reference frame |
| Delay | Seconds in numerical phase calculations | Convert explicitly when displaying ns |
| Calibration frequency | Saved product's axis | Preserve or match it explicitly when applying weights |

## Inputs are not interchangeable with antenna IDs

Use `AntennaMapping` to translate identifiers. Correlator input indices,
physical station names, calibration antenna IDs and weight-array slots are
different namespaces. For the current single-polarization correlator setup,
the relevant signal is `packet_idx`; do not invent a `2 * packet_idx + pol`
mapping from a generic dual-polarization model.

The layout's `functional` flag describes wiring. Its
`include_in_beamforming` flag describes selection in that layout, which may
differ from the actual deployed weights. An analysis across days needs the
appropriate layout and calibration for each interval.

## Frequency and sampling are product properties

The board-side SNAP spectrum spans 4096 channels across 375–500 MHz. The
selected correlator band has 3072 channels; these are distinct products.
The current `layout_64ant` format describes a 137.438953472-second visibility
integration. Historical formats and fast beam products have different cadences.
The source snapshot contains the relevant format files and their hashes.

## A phase check needs its conventions

Baseline orientation, conjugation, geometric steering, calibration weights,
and frequency order must agree. Use packaged functions rather than copying a
phasor sign from another implementation. The same physical operation can have
different signs under different visibility and baseline definitions.

## What the numbers establish

- A rank-1 statistic describes the solve under its selected window and model.
  It is not, by itself, calibrated beam sensitivity.
- High coherence can occur for a stationary contaminant. Multiple references
  and suitable null controls help distinguish sky tracking.
- A solar intensity change may be intrinsic to the Sun.
- A passing injection checks the processing path and parameter range exercised
  by that injection, not the whole telescope's collecting area.

See [check a calibration](check-calibration.md) and the
[canonical knowledge links](../knowledge.md) for interpretation guidance.
