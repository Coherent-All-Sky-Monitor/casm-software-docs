# Read visibilities and plot antenna spectra

A visibility describes how two antenna signals agree. An **autocorrelation**
compares an input with itself and shows its received power. A **cross-correlation**
compares two different inputs and has both amplitude and phase.

Here you will read two antennas, plot their spectra, and select a smaller piece
of the data. Use a notebook with the `casm_offline_env` kernel, or activate it:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
```

## Read two antennas

This example uses files present on the CASM host at review time and a ten-minute
daytime interval on August 19. Give the reader a root directory and a time
window; it finds the observation folders and joins the matching files.
The current recordings use the 64-antenna format, which the reader detects
from their headers. No format configuration is needed for this first example.
For new observations use `/home/casm/software/dev/antenna_layouts/current`.
This historical example keeps the layout matching its recording; do not pair
old data with today's layout without checking the mapping. Antenna numbers are
physical labels; `packet_index()` finds the corresponding inputs in the file.

```python
import numpy as np
from casm_io.correlator import AntennaMapping, read_visibilities

ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-19_bf17.csv"
)
inputs = sorted([ant.packet_index(9), ant.packet_index(10)])
data = read_visibilities(
    data_root="/mnt",
    time_start="2026-08-19 18:04:00",
    time_end="2026-08-19 18:14:00",
    inputs=inputs,
)
print(data.vis.shape)                    # (time, frequency, baseline)
print(data.freq_mhz[[0, -1]], "MHz")
print(data.metadata.get("gaps", []))
```

Times default to UTC and frequencies to descending order. The two-antenna
selection keeps this first read small. Change the root and time window for
your own data; you do not need to find individual files.

For a narrower search, use a root such as `/mnt/nvme4/data/casm`.
`data_dir` is an optional override for a specific observation directory tree.
For old headerless recordings, supply `fmt=load_format("layout_64ant")`
after importing `load_format` from `casm_io.correlator`; choose the appropriate
format for other recording modes. The recording format and antenna layout CSV
serve different purposes: one describes the binary data, the other the wiring.

For two sorted inputs, the three baselines are `(first, first)`,
`(first, second)` and `(second, second)`. Thus the outside columns hold
autocorrelations and the middle column holds the cross-correlation:

```python
auto = data.vis[:, :, [0, 2]].real       # two antenna power spectra
cross = data.vis[:, :, 1]               # their shared signal
freq = data.freq_mhz                    # frequency in MHz
times = data.time_unix                  # Unix seconds, UTC
print(auto.shape, cross.shape)
```

## Plot the power spectra

The existing plotting function averages the selected times and makes one panel
per antenna. Nothing is saved unless you supply an output path.

```python
import matplotlib.pyplot as plt
from casm_vis_analysis.plotting.autocorr import plot_autocorr

labels = [ant.format_antenna(ant.antenna_for_input(p)) for p in inputs]
fig = plot_autocorr(auto, freq, labels, ncols=2,
                    time_unix=times, time_tz="UTC")
plt.show()
```

```{figure} ../_static/tutorials/io/visibility-snap0.png
:alt: Six archived SNAP 0 antenna spectra showing different power levels and narrow frequency peaks.

Existing scratchpad example: SNAP 0, 2026-08-05 05:20:16–10:29:31 UTC.
It uses the same plotting routine for six inputs over a longer interval.
Your two-antenna selection will produce two panels.
```

Read left to right in frequency and compare the smooth background with the
narrow peaks. The panels use a common power scale, so differences are visible.
Power is in instrumental units expressed in dB, not calibrated sky flux.
A stronger spectrum alone does not mean an antenna is more sensitive.

## Zoom in time and frequency

NumPy slices select positions; boolean masks select physical ranges. This keeps
the first ten integrations and the 440–450 MHz channels already in memory:

```python
band = (freq >= 440) & (freq <= 450)
small_cross = cross[:10, band]
small_freq = freq[band]
small_times = times[:10]
print(small_cross.shape, small_freq[[0, -1]], "MHz")
```

For a smaller read from disk, add `freq_range_mhz=(440, 450)` to the original
call. Alternatively, `channels=(0, 128)` reads the first 128 native channels.
Use one of those options. Native order runs from high frequency to low frequency.

## Look at the cross-correlation

Amplitude measures the correlated signal strength. Phase includes geometric
and instrumental delays; a delay produces a slope with frequency. Start with
one integration so time averaging does not wash out a moving fringe:

```python
fig, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 5))
axes[0].plot(freq, np.abs(cross[0]))
axes[0].set_ylabel("Amplitude")
axes[1].plot(freq, np.angle(cross[0]))
axes[1].set_ylabel("Phase (rad)")
axes[1].set_xlabel("Frequency (MHz)")
plt.show()
```

```{figure} ../_static/tutorials/io/cross-phase-sawtooth.png
:alt: Wrapped cross-correlation phase versus frequency for nine baselines referenced to antenna 9, showing repeated jumps between minus pi and pi.

Archived phase spectra from August 23, 2026, 20:42:59–21:40:15 UTC.
Each panel pairs antenna 9 with the antenna named at left. These are
time-averaged, background-subtracted visibilities before Sun fringe-stopping,
not output from the single-integration example above.
```

Follow the 9×19 panel: phase rises across frequency, reaches π, and reappears
at −π. Those jumps are the phase wrapping, not breaks in the signal. Different
baselines have different slopes; instrumental delays also contribute.

Phase wraps between −π and π, so a sawtooth shape can be normal. Avoid averaging
complex values over the whole band before correcting a phase slope: they can
cancel. Check warnings and gaps before treating a quiet interval as a measurement.

Continue with [voltage dumps](read-voltages.md) to see where correlations come
from. [Example sources and technical notes](../developer/io-example-notes.md)
record the archived figure, reviewed code and limits of these examples.
