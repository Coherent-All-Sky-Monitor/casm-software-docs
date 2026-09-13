# Check a calibration with a Cyg A transit

Apply a solar calibration to visibilities and form a beam at one fixed
direction near Cyg A's meridian crossing. As the sky rotates, Cyg A moves
through the beam: its measured power should rise and fall. This checks whether
the calibration produces a plausible response on another source.

## Read an existing transit

```{figure} ../_static/tutorials/transit/cyga_stationary_beam_20260805.png
:alt: Cyg A stationary-beam waterfall and orange power curve rising before transit, peaking shortly after it, and falling back toward the background.

Existing scratchpad result from 2026-08-05. Eighteen antennas were phased
with an August-2 solar calibration toward a fixed direction, altitude
86.43°, azimuth 0.47°. The dashed line marks Cyg A's 06:58 UTC meridian
crossing; the dotted orange line marks the measured power maximum.
```

Read the bottom panel first. The orange curve grows as Cyg A approaches,
peaks near the crossing, then falls toward the background. Its peak was
scaled to one, so this plot shows shape rather than absolute sensitivity.

The top panel shows the same crossing by frequency. A broad bright region
appears around transit across much of the band; horizontal features and
masked strips show why inspecting the waterfall matters alongside the average.
The calculation removed a static visibility background estimated outside
70 minutes either side of transit.

This figure contains measured data and a transit-time marker. It has no
predicted beam curve. Its annotation reports a roughly two-hour crossing
and a peak after meridian transit; these are historical measurements, not
proof of agreement with an exact beam model.

## Plot the saved light curve

You can explore the small saved result without rereading the original
visibilities. In a notebook on the CASM host:

```python
from datetime import datetime, timezone
import numpy as np
import matplotlib.pyplot as plt

path = "/mnt/nvme5/casm_pipeline/scratchpad/cyga_stationary_beam_20260805.npz"
with np.load(path, allow_pickle=False) as saved:
    times = saved["time_unix"]
    power = saved["lc"]
utc = [datetime.fromtimestamp(t, timezone.utc) for t in times]
fig, ax = plt.subplots(figsize=(9, 3))
ax.plot(utc, power / np.nanmax(power))
ax.set(xlabel="Time (UTC)", ylabel="Power / peak")
fig.autofmt_xdate()
plt.show()
```

This redraws the bottom curve with simple labels. The original figure above
adds the frequency panel and transit annotations.

## Form the beam from another observation

1. Select visibilities before, during and after Cyg A's crossing, an existing
   calibration, and the antenna layout for that epoch.
2. Apply the same antenna set, channel mask and background treatment to each
   calibration being compared. Keep the beam direction fixed throughout.
3. Plot power against time with the expected crossing time marked. Inspect
   the waterfall for broadband support, interference and missing data.
4. Compare with an exact array-factor prediction and a separately checked
   off-source direction before interpreting a timing or width discrepancy.

The existing visibility-analysis module performs the beam sum. With prepared
`data` (raw, or consistently static-subtracted), `ant` (the selected mapping)
and `cal` (loaded calibration), the central call is:

This function needs the full correlator triangle, not the two-input subset
from the first tutorial. Use the linked input-preparation example for this step.

```python
from casm_vis_analysis.beam_power import beam_power_vs_time, plot_beam_power

result = beam_power_vs_time(
    data, ant,
    sources=[("Cyg A fixed beam", fixed_alt_deg, fixed_az_deg)],
    cal_weights=cal, freq_band_mhz=(low_mhz, high_mhz), sign=-1,
)
figure = plot_beam_power(result, time_tz="UTC")
```

Choose the fixed angles from the selected observation, not from the August
example. Passing `"cyg-a"` instead of the tuple would track the source and
change this experiment. The function returns cross-baseline power and does
not subtract a background by itself. This illustrative call does not reproduce
the historical plot's masking and preprocessing automatically.

The [input preparation example](../developer/imaging-notes.md#1-select-a-small-fully-described-input)
shows the required objects and checks. Start there with a few integrations,
then budget a longer read for the complete transit.

## What can you conclude?

A broad crossing with support across frequencies is useful evidence that
the calibration and steering produce a response near Cyg A. It does not
establish an absolute sensitivity, validate every sky direction, or explain
all asymmetry in the curve. Without a predicted response and controls, a
shifted peak alone does not identify a calibration fault.

For complementary frequency-by-frequency inspection, use the
[baseline phase example](solar-phase.md). Sky imaging is a separate
[optional tutorial](image-visibilities.md).
The [cross-day calibration example](../developer/calibration-transfer-notes.md)
shows how to compare baseline phase residuals using the same saved weights.

The [transit example notes](../developer/transit-example-notes.md) preserve
the original script's processing details, evidence paths and checksums. This
page reuses the saved scratchpad result; no new telescope analysis was run.
