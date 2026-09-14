# Array shapes, units and antenna IDs

Use this reference when an array dimension, frequency axis or antenna label
is unclear. The [first visibility tutorial](read-visibilities.md) introduces
these ideas through a worked example.

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

The `layout_64ant` format describes itself as 128 inputs (64 antennas x 2
polarizations) and the file's visibility axis is the full upper triangle of
those 128 signals. The site wires one polarization per antenna into 4 SNAPs of
12 ADCs, so only indices 0-47 carry sky. `packet_index = snap_id * 12 + adc` is
that index directly, and it is what the reader's `ref`, `targets` and `inputs`
arguments take.

One antenna through every namespace, on
`/home/casm/software/dev/antenna_layouts/current`:

| antenna | SNAP/ADC | `packet_index` | `format_antenna` | layout row/col | part number |
|---|---|---|---|---|---|
| 9 | SNAP 0, ADC 8 | 8 | `Ant 9 \| S0A8 → input 8` | N21, E1 | ANT00009 |

The layout's `functional` flag describes wiring. Its
`include_in_beamforming` flag describes selection in that layout, which may
differ from the actual deployed weights. An analysis across days needs the
appropriate layout and calibration for each interval.

## Frequency and sampling are product properties

The board-side SNAP spectrum spans 4096 channels across 375–500 MHz. The
selected correlator band has 3072 channels; these are distinct products.
The current `layout_64ant` format describes a 137.438953472-second visibility
integration. Historical formats and fast beam products have different cadences.

## A phase check needs its conventions

Baseline orientation, conjugation, geometric steering, calibration weights,
and frequency order must agree. Use packaged functions rather than copying a
phasor sign from another implementation. The same physical operation can have
different signs under different visibility and baseline definitions.

See [check a calibration](check-calibration.md) and the
[canonical knowledge links](../knowledge.md) for interpretation guidance.
