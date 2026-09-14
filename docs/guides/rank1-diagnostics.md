# Solve a solar calibration and plot rank-1 against frequency

The rank-1 ratio `sigma_1 / sigma_2` says how well a single coherent component
explains the visibility matrix at one channel. Here you run the production
solar solve end to end on an archived window, then plot the ratio the solve
produced.

The chain is the one in the wiki recipe: read the transit window, subtract a
night static template, fringe-stop to the Sun, solve per channel with the SVD
calibrator. Activate the environment first:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
```

This reads a full hour of the 128-input triangle, 5.3 GB of visibilities. Peak
resident memory is 17 GB, reached inside the reader, and the whole chain takes
about 15 s on the correlator host. Do not run it on a laptop.

## Read the solve window

Settings come from an existing build,
`/mnt/nvme5/vishnu/cal_build_20260824/params_aug23_exact512.json`: 16 antennas,
reference antenna 9, Sun window 20:41:30-21:41:30 UTC on August 23, 2026. Record
where that window sits relative to the Sun's altitude maximum; window placement
moves both the ratio and the beam.

```python
import numpy as np
from astropy.time import Time
from casm_io.correlator import AntennaMapping, read_visibilities
from casm_vis_analysis.sources import source_altaz

# Sun altitude maximum on the solve day, 1-minute grid.
day_start = Time("2026-08-23 00:00:00", scale="utc").unix
grid = day_start + np.arange(0.0, 86400.0, 60.0)
alt_deg, _ = source_altaz("sun", grid)
peak = Time(grid[int(np.argmax(alt_deg))], format="unix")
print("Sun peak (UTC):", peak.utc.iso, round(float(alt_deg.max()), 1), "deg")

solve_antennas = [9, 10, 15, 19, 22, 23, 24, 26, 30, 32, 36, 38, 40, 42, 44, 45]
ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)
ant = ant.with_inactive(
    [a for a in ant.active_antennas() if a not in solve_antennas]
)

data = read_visibilities(
    data_dir="/mnt/nvme4/data/casm/visibilities_64ant",
    time_start="2026-08-23 20:41:30", time_end="2026-08-23 21:41:30",
    time_tz="UTC", workers=1, verbose=False,
)
print(data.vis.shape, round(data.vis.nbytes / 1e9, 1), "GB")  # time, freq, baseline
print(data.freq_mhz[[0, -1]], "MHz", data.metadata.get("gaps"))
```

The printed peak is 19:56 UTC at 64.0 deg, so this window starts 45 min after
the peak and the Sun falls from 62.0 to 54.8 deg across it. Window placement
changes the resulting fold S/N materially (wiki `recipes.md` step 0).

Read the full native triangle. Fringe stopping rejects `inputs=` subtriangles,
because subtriangle ranks are not packet indices, and the SVD needs the full
N x N matrix. 26 integrations arrive, 20:42:59 to 21:40:15 UTC.

## Subtract the night static

A static template is the array's own quiet-sky signal: cross-talk and standing
correlation that is present with or without the Sun. Subtracting it keeps that
pedestal out of the solve matrix, where it inflates the secondary singular
values (wiki `recipes.md` step 5). The template must come from the adjacent
night and from the same EQ/gain state; statics age fast
and are void across any F-engine re-sync.

```python
from casm_vis_analysis.offsource import (load_static_visibility,
                                         subtract_static_visibility)

static = load_static_visibility(
    "/mnt/nvme5/vishnu/cal_build_20260824/static_aug23_exact512_CAL0823N.npz"
)
# Same channels, or the subtraction is meaningless.
assert np.array_equal(static["freq_mhz"], data.freq_mhz)
clean = subtract_static_visibility(data, static["static_vis"])
del data          # the raw cube is 5.3 GB and is not needed again
```

This template averages 2026-08-24 03:00-03:30 UTC, the first clean night window
after the transit that does not straddle overlapping observations.

## Fringe-stop to the Sun

```python
from casm_vis_analysis.fringe_stop import fringe_stop, auto_detect_sign

fs = fringe_stop(clean, ant, ref_ant=9, source="sun", sign=-1, min_alt_deg=10.0)
print(int(fs["time_mask"].sum()), "integrations with the Sun above 10 deg")

k = list(fs["target_aids"]).index(19)   # baseline 9 x 19
print("sign check:", auto_detect_sign(fs["vis"][:, :, k], fs["freq_mhz"],
                                      fs["tau_s"][:, k]))
```

`sign=-1` is the CASM convention and is not negotiable: at `-1` the
fringe-stopped phase stays coherent (wiki records 0.99 against about 0.2 at
`+1`), and `auto_detect_sign` re-derives `-1` from this baseline. All 26
integrations pass the 10 deg altitude gate.

## Solve

```python
from casm_calibrator import SVDConfig, svd_calibrate
from casm_calibrator.svd import SVDMode

cal = svd_calibrate(
    fs, ant, data=clean,
    config=SVDConfig(threshold=1.0, svd_mode=SVDMode.PHASE_ONLY,
                     block_size=1, masked_band_strategy="zero"),
)
print(len(cal["ant_ids"]), "antennas,", len(cal["freqs_mhz"]), "channels,",
      int(np.asarray(cal["flags"]).sum()), "channels solved")
```

`threshold=1.0` accepts every channel that carries signal, `block_size=1` solves
each channel separately, and `masked_band_strategy="zero"` zeroes RFI-flagged
channels instead of extrapolating gains over them. It only does so when a mask
reaches the solve: the production driver `make_cal_and_weights` calls
`fringe_stop` without `rfi_mask` and never calls `apply_rfi_mask`, so there
"zero" is inert. Pass `rfi_mask` to `fringe_stop` (or `apply_rfi_mask`) to mask,
as [mask RFI and fit per-antenna delays](rfi-and-delay.md) shows.

The reference antenna reaches the solver through `fs`, not through
`SVDConfig.ref_ant_idx`. `svd_calibrate` reads `fs["ref_ant"]`, finds its
position in the sorted active set and overwrites `ref_ant_idx` with that index.
Setting `ref_ant_idx` on the config has no effect.

## Plot the ratio

```python
import matplotlib.pyplot as plt

freq = np.asarray(cal["freqs_mhz"])
ratio = np.asarray(cal["rank1_ratios"])
n_ant = len(cal["ant_ids"])
sun_band = (freq >= 435) & (freq <= 460)

fig, ax = plt.subplots(figsize=(8, 3.2))
ax.axvspan(465.3, 466.7, color="0.8", lw=0)        # 466 MHz satellite emitter
ax.plot(freq, ratio, lw=0.5, color="C0")
ax.axhline(n_ant - 1, color="k", ls="--", lw=0.8)
ax.text(freq.min(), n_ant - 0.6, f"coherent limit N-1 = {n_ant - 1}", fontsize=8)
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel(r"Rank-1 ratio $\sigma_1/\sigma_2$")
ax.set_ylim(0, n_ant + 1)
fig.tight_layout()
plt.show()

print("median", round(float(np.nanmedian(ratio)), 2),
      "| 435-460 MHz", round(float(np.nanmedian(ratio[sun_band])), 2))
```

```{figure} ../_static/tutorials/calibration/rank1-vs-freq.png
:alt: Rank-1 ratio against frequency for the 16-antenna August 23 solar solve, rising to about 10 across the 435 to 460 MHz sun band and dropping below 4 at the band edges.

Output of the code above: 16 antennas, 26 integrations, 2026-08-23
20:42:59-21:40:15 UTC, night static subtracted. The grey stripe marks the
465.3-466.7 MHz satellite emitter. Rendered by
`scripts/render_rank1_tutorial.py`.
```

Median 5.87 over the full band, 9.18 across 435-460 MHz where the Sun dominates.
The ceiling for 16 antennas is 15. A single median hides the structure: the ratio
collapses at the band edges, where the analogue response rolls off, and dips to
3.89 in the 465.3-466.7 MHz emitter band.

## Singular spectrum

The in-memory result carries `singular_values` (channels x antennas), so the
driver's renderer works directly on it. Saved HDF5/NPZ calibrations do not keep
the spectrum.

```python
from bf_weights_generator.recipe_diagnostics import plot_svd_vs_freq

path, stats = plot_svd_vs_freq(
    cal, "svd-vs-freq.png",
    "Sun 2026-08-23 20:41:30-21:41:30 UTC, 16 antennas, phase-only, night static",
)
print(stats)
```

```{figure} ../_static/tutorials/calibration/svd-vs-freq.png
:alt: Left panel, the six largest singular values against frequency on a log scale; right panel, the leading singular-value fraction against frequency near 0.5 in the sun band.

Output of the code above. sigma_1 median 14.68 against the coherent value 15;
rank-1 fraction median 0.470 against the coherent value 0.5.
Rendered by `scripts/render_rank1_tutorial.py`.
```

## What the number means

At each channel the solver builds the antenna-by-antenna matrix, replaces every
entry by its phase, and zeroes the autocorrelation diagonal. A perfectly
coherent point source then gives the all-ones matrix minus the identity, whose
singular values are `N-1, 1, ..., 1`. The ideal ratio is therefore `N-1` (15
here) and the ideal rank-1 **fraction** `sigma_1 / sum(sigma)` is **0.5**, not 1.
The measured 0.470 sits close to that ceiling; the fraction cannot reach 1 for
this matrix.

Dead channels do not produce a large ratio. Nonfinite visibilities in the
selected integrations raise before any SVD runs
(`casm_calibrator/matrix.py:122-123`); a finite all-zero channel is not
rejected there, and its largest singular value is exactly zero, so the solver
skips it and leaves ratio 0 with the channel unflagged. See the [developer
notes](../developer/svd-notes.md).

**Do not rank calibrations by this number.** On sky the higher-ratio cal folded
B0329 worse than the lower-ratio one, so the ratio measures the rank-1 fit to
the Sun matrix and not the phase solution elsewhere (wiki
`rank1-metric-caveat.md` has the paired numbers). Adjudicate cal variants with the Cyg A referee instead, and compare
ratios across epochs only at matched window placement and integration count.

## Mask the 465 MHz emitter

A narrowband satellite emitter sits at 465.3-466.7 MHz and depresses the ratio
there. Flag the band before solving:

```python
from casm_vis_analysis.rfi import RFIMask

rfi = RFIMask(bad_ranges_mhz=[(465.3, 466.7)], label="sat-466")
print(int(rfi.flag_bins(cal["freqs_mhz"]).sum()), "channels flagged")
# fringe_stop(clean, ant, ref_ant=9, source="sun", sign=-1, rfi_mask=rfi)
# carries the mask on fs['freq_mask']; masked_band_strategy="zero" then
# sets gains 0 and flags False at those 46 channels.
```

`RFIMask` returns True for good channels when called, which is the convention
`fringe_stop(rfi_mask=...)` expects. Alternatively call
`casm_vis_analysis.rfi.apply_rfi_mask(clean, rfi)`, which writes
`clean['freq_mask']` with True = flagged, and leave `rfi_mask=None`;
`fringe_stop` picks that mask up and inverts it. `SVDConfig` has no band list
of its own; it only decides what happens at channels the mask already flagged. Bursts in this band also damage
individual integrations, so check the per-integration autocorrelations as well
(wiki `rfi-flagging-465mhz.md`).

Next, [watch Cyg A cross a fixed beam](check-calibration.md) to test whether a
calibration actually beamforms.
