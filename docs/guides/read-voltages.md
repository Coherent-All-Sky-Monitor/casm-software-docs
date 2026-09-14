# Read a voltage dump

A voltage dump saves short stretches of the antenna signals before they are
averaged into visibilities. You can inspect one input's power spectrum or
correlate a pair of inputs at a time resolution you choose.

This walkthrough reads a dump already on disk. Use a notebook with the
`casm_offline_env` kernel, or activate the environment:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
```

## Open an existing dump

Use `cand_dumps`: candidate-triggered voltage dumps land in
`/mnt/nvme4/data/casm/cand_dumps/stream_N/` on the node that served the stream
(`casm_t2.beams.VOLTAGE_DUMP_DIR`). `/mnt/nvme3/data/casm/voltage_dumps` holds
older dumps with no reaper. `beam_dumps` are beamformer output rather than
voltages; convert those with
[beam dump to filterbank](beamdump-to-filterbank.md).

The dump directory contains `stream_0`, `stream_1`, and other stream folders.
Each stream holds part of the frequency band. Copy the full filename prefix
before `.000000.dada`, including its byte offset when present, to identify one
dump. This avoids combining separate dumps from the same observation.

```python
from casm_io.voltage import VoltageReader
from casm_io.voltage.header import parse_dada_header
from pathlib import Path

data_dir = "/mnt/nvme4/data/casm/cand_dumps"
prefix = "2026-08-02-14:32:06_0205375108055040"
dump = Path(data_dir) / "stream_1" / f"{prefix}.000000.dada"
header = parse_dada_header(str(dump))  # reads only the 4096-byte header
print({k: header[k] for k in ("DUMP_UTC_START", "NCHAN", "TSAMP", "RESOLUTION")})
assert header["NCHAN"] == "512" and header["RESOLUTION"] == "67584"
reader = VoltageReader(data_dir, prefix)
print("Streams found:", reader.subbands_found)
```

Start small. This reads 0.01 seconds from one available stream and SNAP 0:

```python
stream = 1
result = reader.read_full_band(
    subbands=[stream], snaps=[0], seconds=0.01,
)
v = result.voltages[0]
freq = result.freq_mhz
print(v.shape)                           # (time, frequency, ADC input)
print(freq[[0, -1]], "MHz")
print("Zero-filled streams:", result.filled_subbands)
```

The last axis contains 12 ADC inputs on the chosen SNAP. Each value is complex:
its real and imaginary parts come from the recorded 4-bit samples. For current
stream dumps, time samples are 32.768 microseconds apart and each stream has
512 frequency channels. `filled_subbands` lists the selected stream indices that
had no data on disk and were zero-filled, with a warning; a selection with no
data at all raises instead.

SNAP/ADC labels are hardware addresses, not antenna IDs.

## Bridge SNAP/ADC to antenna numbers

Pass `antenna_csv=` to have the reader do the wiring lookup. The voltages then
come back as one array indexed by antenna instead of a dict keyed by SNAP:

```{code-block} python
by_ant = reader.read_full_band(
    antenna_csv="/home/casm/software/dev/antenna_layouts/current",
    subbands=[1], snaps=[0], seconds=0.01,
)
v_ant = by_ant.voltages                  # (time, frequency, antenna) complex64
print(v_ant.shape, by_ant.antenna_df["antenna_id"].tolist()[:5])
```

The antenna axis follows the CSV row order, returned as `by_ant.antenna_df`.
Antennas on a SNAP that was not loaded come back as zeros, so this `snaps=[0]`
read fills only the SNAP 0 antennas; drop `snaps=` to get all of them. Rows
outside the hardware layout (`snap_id` or `adc` out of range) raise before any
indexing.

## Make an autocorrelation spectrum

Square the voltage magnitude and average over time. This gives the mean power
at each frequency for each input, just as in the existing voltage notebook:

```python
import numpy as np
import matplotlib.pyplot as plt

power = np.mean(np.abs(v) ** 2, axis=0)    # (frequency, ADC input)
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(freq, power[:, 0])                # ADC input 0
ax.set(xlabel="Frequency (MHz)", ylabel="Mean |v|²",
       title="SNAP 0 · ADC 0")
plt.show()
```

```{figure} ../_static/tutorials/io/voltage-single-stream.png
:alt: Mean voltage power for SNAP 0 ADC 0 over stream 1.

Output of the code above: the first 305 samples (9.99424 ms) of the dump
starting 2026-08-03 18:11:41.810 UTC, stream 1, SNAP 0, ADC 0.
```

The caption's start time is the header's `DUMP_UTC_START`, the first sample of
this dump. It runs later than the observation's `UTC_START`, which the dump's
`OBS_OFFSET` bytes are counted from.

Inspect narrow spikes and broad changes across this single stream. Power is
in instrumental sample units. No calibration or interference mask is applied.
The returned voltage array is only 14,991,360 bytes.

## Choose a later interval or a frequency range

To read a later part of the dump, add `offset_seconds=0.1` to the read call.
`seconds` controls how much is read; it does not average samples. To read more
of the band, supply adjacent streams such as `subbands=[1, 2]` when present.

Once loaded, ordinary slices work as they did for visibilities:

```python
first_samples = v[:100, :, 0]             # first 100 times, ADC 0
band = (freq >= 440) & (freq <= 450)
narrow = v[:, band, 0]                   # may be empty for another stream
print(first_samples.shape, narrow.shape)
```

## Form a cross-correlation

Use the existing correlator rather than writing another one. The following
compares ADCs 0 and 2 on SNAP 0, averaging into approximately 1 ms bins:

```python
from casm_io.voltage import correlate

corr = correlate(result.voltages, inputs=[(0, 0), (0, 2)], tint_s=0.001)
auto0 = corr.vis[:, :, 0, 0].real
cross02 = corr.vis[:, :, 0, 1]
print(corr.vis.shape)                    # (time bin, channel, input, input)
print(corr.tint_samples, "samples per bin")
print(corr.time_s[:3], "seconds from this read's start")
```

The function multiplies the signals first, then averages the products. Averaging
voltages first would discard the changing signal you are trying to correlate.
Its time axis is relative seconds, not Unix time. For longer dumps, use
`reader.iter_full_band(...)` to read chunks instead of loading everything at once.

## Provenance

The autocorrelation figure reuses `casm_io/examples/voltage_quickstart.ipynb`,
cell 13 (August 3, 11:06:52–11:06:54 PDT, stream 1, SNAP 0). Streams 0/3/4/5
are zero-filled in that dump; only streams 1–2 carry data, so `subbands=[1]`
above matches the populated stream. The notebook is not run sequentially end
to end here: it is reused only to show the plotted quantity and panel layout,
not as a live acquisition record.
