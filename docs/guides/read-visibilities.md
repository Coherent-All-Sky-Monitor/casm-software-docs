# Read visibilities and plot antenna spectra

A visibility describes how two antenna signals agree. An **autocorrelation**
compares an input with itself and shows its received power. A **cross-correlation**
compares two different inputs and has both amplitude and phase.

Here you will read two antennas, plot their spectra, and select a smaller piece
of the data. Use a notebook with the `casm_offline_env` kernel, or activate it:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
```

## Find a recording

`discover_observations(data_dir, fmt=None, verbose=False)` scans one directory of
`.dat` files and returns a list of dicts with `base_str`, `n_files`, `time_start`,
`time_end`, `fmt` and `data_dir`, sorted by start time. Headerless recordings need
an explicit `fmt` and are otherwise skipped.

```{code-block} python
from casm_io.correlator import discover_observations

for obs in discover_observations("/mnt/nvme4/data/casm/visibilities_64ant"):
    print(obs["base_str"], obs["n_files"], obs["time_start"], obs["time_end"])
```

The same survey from the shell, as a table with UTC and Pacific spans:

```bash
casm-viz-data-span --data-dir /mnt/nvme4/data/casm/visibilities_64ant \
  --format layout_64ant
```

## Read two antennas

This example uses files present on the CASM host at review time and a ten-minute
daytime interval on August 23. Give the reader a root directory and a time
window; it finds the observation folders and joins the matching files.
The current recordings use the 64-antenna format, which the reader detects
from their headers. No format configuration is needed for this first example.
For new observations use `/home/casm/software/dev/antenna_layouts/current`.
This historical example keeps the layout matching its recording; do not pair
old data with today's layout without checking the mapping. Antenna numbers are
physical labels; `packet_index()` finds the corresponding inputs in the file.
Antenna 9 is the reference antenna every CASM solar solve fringe-stops against
(casm-wiki `recipes.md`, `ref_ant=9`), so later tutorials reuse this baseline;
antenna 19 is the other end of it.

```python
import numpy as np
from casm_io.correlator import AntennaMapping, read_visibilities

ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)
inputs = sorted([ant.packet_index(9), ant.packet_index(19)])
data = read_visibilities(
    data_root="/mnt/nvme4/data/casm",
    time_start="2026-08-23 20:42:00",
    time_end="2026-08-23 20:52:00",
    inputs=inputs,
)
print(data.vis.shape)                    # (time, frequency, baseline)
print(data.freq_mhz[[0, -1]], "MHz")
print(data.metadata.get("gaps", []))
```

Times default to UTC and frequencies to descending order. The two-antenna
selection keeps this first read small. Change the root and time window for
your own data; you do not need to find individual files.

Use `data_root="/mnt"` to search across mounted data disks.
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

```{figure} ../_static/tutorials/io/visibility-two-antennas.png
:alt: Antenna 9 and antenna 19 power spectra from the ten-minute selection, with narrow peaks above their smooth backgrounds.

Output of the code above: antenna 9 and antenna 19, averaged over the selected
integrations on August 23, 2026. No calibration or frequency mask is applied.
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
fig.tight_layout()
plt.show()
```

```{figure} ../_static/tutorials/io/cross-amplitude-phase.png
:alt: Single-integration amplitude and wrapped phase versus frequency for the antenna 9 by antenna 19 cross-correlation.

Output of the code above: the first integration in the same antenna 9 × 19
selection. These are raw cross-correlations, before background subtraction,
fringe-stopping or calibration.
```

Follow the phase between its jumps at ±π: those jumps are phase wrapping, so a
sawtooth is the normal appearance of a delay slope. Narrow-band interference and
noisy channels interrupt the slope. Averaging complex values over the whole band
before the slope is corrected makes them cancel. Check warnings and gaps before
treating a quiet interval as a measurement.

## Exclude the 465 MHz emitter

A narrowband satellite emitter sits at 465.3–466.7 MHz and damages any average
that includes it (casm-wiki `rfi-flagging-465mhz.md`). Drop the band before
plotting or averaging:

```{code-block} python
from casm_vis_analysis.rfi import RFIMask

mask = RFIMask(bad_ranges_mhz=[(465.3, 466.7)], label="emitter_465")
good = mask(freq)                        # True = keep this channel
mean_cross = cross[:, good].mean(axis=1)  # band average without the emitter
```

`RFIMask` ships no default band list: pass the ranges, or load the versioned
config with `RFIMask.from_static()`. Masking for a solve is covered in
[mask RFI and fit delays](rfi-and-delay.md).

Continue with [voltage dumps](read-voltages.md) to see where correlations come
from.

## Provenance

Data: `/mnt/nvme4/data/casm`, `visibilities_64ant/2026-08-23-19:18:14.dat.1`,
20:42–20:52 UTC on 2026-08-23 (actual integrations 20:42:59–20:49:51 UTC).
Antenna mapping: `casm_antenna_layout_2026-08-07.csv`, the layout in force for
this recording (antennas 9/19 map to inputs 8/18). Figures rendered by
`scripts/render_visibility_tutorial.py`, which executes every displayed block
in this page and saves the plots in place of `plt.show()`.
