# Mask RFI and fit per-antenna delays

This page builds an RFI mask, fringe-stops a 20-minute solar window with it, and fits one
delay per antenna against the reference.

Follow [seeing the Sun in baseline phase](solar-phase.md) first: that page ends
with fringe-stopped bands that are nearly horizontal in time but still sloped
in frequency. That slope is the delay fitted here.

## Pick the window around the Sun peak

Read the full native triangle. `fringe_stop` slices the reference-to-target
baselines itself and rejects `inputs=` subtriangles, whose ranks are not packet
indices.

```python
import numpy as np
from astropy.utils import iers
from casm_io.correlator import AntennaMapping, read_visibilities
from casm_vis_analysis.sources import source_altaz

day = "2026-08-23"
ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)

# Sun altitude on a 1-min grid over the 12 h from 16:00 UTC, to place the window.
grid_utc = np.datetime64(f"{day}T16:00:00") + np.arange(12 * 60) * np.timedelta64(60, "s")
grid = grid_utc.astype("datetime64[s]").astype(float)   # unix seconds
with iers.conf.set_temp("auto_download", False), iers.conf.set_temp("auto_max_age", None):
    alt_deg, _ = source_altaz("sun", grid)
peak = grid[int(np.argmax(alt_deg))]
print("Sun peak:", np.datetime64(int(peak), "s"), "UTC, alt", round(alt_deg.max(), 2), "deg")

data = read_visibilities(
    data_root="/mnt/nvme4/data/casm",
    time_start=f"{day} 19:46:00", time_end=f"{day} 20:06:00",
    time_tz="UTC", workers=1,
)
print(data.vis.shape)            # time, frequency, full upper triangle
print(data.metadata["files"])
```

The peak is 19:56:00 UTC at altitude 63.99 deg, so 19:46-20:06 is centred on it.
Record that offset: window placement relative to the peak changes a solve, and
a peak-centred window is not automatically the best one
(casm-wiki `recipes.md` step 0). The read returns 8 integrations at 137.44 s,
19:48:00 to 20:04:02 UTC, as `(8, 3072, 8256)` complex64, 1.6 GB. Peak memory
for the whole page is 9.7 GB; run it on a host with room.

## Build the mask

The module ships no automatic default: `casm_vis_analysis.rfi` requires the
caller to supply the bands. Use the line list the canonical weights build uses,
`bf_weights_generator.recipe_diagnostics.RFI_LINES`, and add the 465.3-466.7 MHz
band on top of it.

```python
from casm_vis_analysis.rfi import RFIMask, apply_rfi_mask
from bf_weights_generator.recipe_diagnostics import RFI_LINES

mask = RFIMask(bad_ranges_mhz=RFI_LINES + [(465.3, 466.7)],
               label="recipe_lines+465mhz")
apply_rfi_mask(data, static=mask)
print(mask.bad_ranges_mhz)
print(int(data["freq_mask"].sum()), "of", len(data.freq_mhz), "channels flagged")
```

308 of 3072 channels are flagged, 10% of the band. `apply_rfi_mask` writes
`data["freq_mask"]` with True = flagged and never touches `data["vis"]`.
Polarity flips downstream: `fringe_stop` stores the inverse, True = good, which
is what `fit_delay` and the plotters expect.

`RFIMask.from_static()` loads the versioned JSON in the package instead. Version 3
flags 2122 of 3072 channels and leaves only 405-434 MHz, which removes the whole
435-460 MHz solar band. It is an imaging-side mask, not the list for a solar solve.

```python
import matplotlib.pyplot as plt
from casm_io.correlator.baselines import triu_flat_index
from casm_vis_analysis.plotting.autocorr import plot_autocorr

n_inputs = data.metadata["nsig"]
auto_col = triu_flat_index(n_inputs, ant.packet_index(9), ant.packet_index(9))
fig = plot_autocorr(data.vis[:, :, [auto_col]].real, data.freq_mhz,
                    [ant.format_antenna(9)], ncols=1,
                    time_unix=data.time_unix, time_tz="UTC")
for lo, hi in mask.bad_ranges_mhz:
    fig.axes[0].axvspan(lo, hi, color="tab:red", alpha=0.18, lw=0)
plt.show()
```

```{figure} ../_static/tutorials/delay/rfi-mask-spectrum.png
:alt: Antenna 9 power spectrum from 391 to 484 MHz with five red bands shaded over the flagged frequency ranges.

Output of the code above: antenna 9 autocorrelation averaged over the eight
integrations, with the five flagged ranges shaded. Power is in instrumental dB.
```

Four of the five bands sit on a spike: 19.3 dB above the local median at
400-402 MHz, 20.0 dB at 436.5-438.5, 9.7 dB at 450-452, 31.3 dB at 462-464.
The 465.3-466.7 MHz band shows 0.2 dB on this day, because the emitter is the
EOS-6 satellite and it is not passing (casm-wiki `sat-id-466mhz-eos6.md`).
Flag it anyway: on 2026-08-19 a pass there wrecked about 32 channels of an
hour-long solve, and the mask is cheap. Two rules come with it:

- Flag the affected **integrations** as well as the channels. The damage rides
  into the hour-average: per-integration rank-1 dip/base was 0.874 that day,
  hour-averaged 0.579. Drop the bad integrations from `data["time_mask"]`
  before fringe stopping when the autos show a burst.
- Never extrapolate a solution across measured channels. The production
  driver `make_cal_and_weights` sets `masked_band_strategy="zero"`, but it
  calls `fringe_stop` with no `rfi_mask` and never calls `apply_rfi_mask`, so
  every channel is marked good and "zero" acts on nothing there. To actually
  mask, pass `rfi_mask` to `fringe_stop` (or `apply_rfi_mask`) as this page
  does.

## Fringe-stop with the mask

```python
from casm_vis_analysis.fringe_stop import fringe_stop, coherence_metric

with iers.conf.set_temp("auto_download", False), iers.conf.set_temp("auto_max_age", None):
    fs = fringe_stop(data, ant, ref_ant=9, source="sun", sign=-1, rfi_mask=mask)

coh = coherence_metric(fs["vis_stopped"], fs["freq_mask"])   # (T, n_bl)
coh_bl = np.nanmean(coh[fs["time_mask"]], axis=0)
for aid, c in zip(fs["target_aids"], coh_bl):
    print(f"{ant.format_antenna(aid):<28} coherence {c:.3f}")
```

Sign must be -1 (casm-wiki `conventions-data.md`). `coherence_metric` averages
unit phasors **over frequency**, so it reads 0.018 to 0.809 here: a 200 ns delay
wraps the phase 19 times across 93.75 MHz and the phasors cancel. Judge antenna
health on the fringe-stopped coherence, never on raw `|corr|`, and read the
values after the delay is removed (next section), where a good antenna sits near
0.99. The full-window time-domain variant used for triage is in casm-wiki
`antenna-health-triage.md`.

## Fit one delay per antenna

The baselines are reference-to-target, so each fitted baseline delay is already
that antenna's delay relative to antenna 9.

```python
from casm_vis_analysis.delay import fit_delay, apply_delay

params = fit_delay(fs["vis_stopped"], fs["freq_mhz"],
                   time_mask=fs["time_mask"], freq_mask=fs["freq_mask"],
                   model="linear")
coh_fixed = np.nanmean(
    coherence_metric(apply_delay(fs["vis_stopped"], fs["freq_mhz"], params),
                     fs["freq_mask"])[fs["time_mask"]], axis=0)

print(f"{'ant':>4} {'snap':>6} {'delay_ns':>9} {'r2':>6} {'pk/2nd':>7} {'coh':>6}  flag")
for aid, tau, r2, pk, c, bad in zip(
        fs["target_aids"], params["delay_ns"], params["r_squared"],
        params["peak_to_secondary_ratio"], coh_fixed, params["low_quality"]):
    snap = f"S{ant.snap_adc(aid)[0]}A{ant.snap_adc(aid)[1]}"
    print(f"{aid:4d} {snap:>6} {tau:+9.2f} {r2:6.3f} {pk:7.2f} {c:6.3f}"
          f"  {'low quality' if bad else ''}")
```

| ant | snap | delay (ns) | r2 | pk/2nd | coherence after | flag |
|---|---|---|---|---|---|---|
| 1 | S0A0 | +990.42 | 0.003 | 1.02 | 0.025 | low quality |
| 3 | S0A2 | -889.47 | 0.004 | 1.17 | 0.022 | low quality |
| 7 | S0A6 | -531.15 | 0.004 | 1.03 | 0.026 | low quality |
| 10 | S0A9 | +1.53 | 0.481 | 2.62 | 0.420 | low quality |
| 12 | S0A11 | -17.53 | 0.674 | 1.24 | 0.330 | low quality |
| 14 | S1A1 | +216.18 | 0.053 | 1.03 | 0.048 | low quality |
| 15 | S1A2 | +215.38 | 0.845 | 5.04 | 0.989 | |
| 18 | S1A5 | +229.61 | 0.694 | 4.02 | 0.976 | low quality |
| 19 | S1A6 | +223.63 | 0.608 | 3.90 | 0.965 | low quality |
| 22 | S1A9 | +225.30 | 0.747 | 6.24 | 0.988 | |
| 23 | S1A10 | +212.29 | 0.743 | 6.42 | 0.961 | |
| 24 | S1A11 | +217.13 | 0.748 | 4.73 | 0.962 | |
| 26 | S2A1 | +48.30 | 0.836 | 8.34 | 0.955 | |
| 27 | S2A2 | +21.96 | 0.660 | 3.49 | 0.884 | low quality |
| 30 | S2A5 | -65.75 | 0.313 | 1.01 | 0.027 | low quality |
| 32 | S2A7 | +32.50 | 0.666 | 4.25 | 0.899 | low quality |
| 33 | S2A8 | -996.52 | 0.250 | 1.07 | 0.034 | low quality |
| 36 | S2A11 | +41.48 | 0.815 | 4.37 | 0.959 | |
| 38 | S3A1 | +129.86 | 0.716 | 5.83 | 0.827 | |
| 40 | S3A3 | +132.13 | 0.616 | 5.45 | 0.903 | low quality |
| 42 | S3A5 | +124.11 | 0.427 | 2.41 | 0.897 | low quality |
| 44 | S3A7 | +130.95 | 0.679 | 4.42 | 0.863 | low quality |
| 45 | S3A8 | +115.55 | 0.648 | 3.74 | 0.875 | low quality |

Removing the fitted delay lifts the frequency coherence of a healthy antenna
from under 0.1 to 0.96-0.99, which is the wiki's good-antenna number. Antennas
1, 3, 7 and 14 stay under 0.05 and their delays sit near the ±1000 ns search
edge with r2 ≈ 0.004: no signal to fit. The full gated-out set in this layout
epoch (`functional` 1, `include_in_beamforming` 0 in
`casm_antenna_layout_2026-08-07.csv`) is 1, 3, 7, 14, 18, 27. Antennas 30 and 33 are the case to be careful
with: they carry solar signal but their phase is not one linear delay, so
`peak_to_secondary_ratio` ≈ 1 and the fit is a coin flip. Read `low_quality`
first: it marks a failed fit, and antenna health is a separate question
(casm-wiki `antenna-health-triage.md`). With 8 integrations, r2 between 0.6 and
0.75 is normal and the delay is still well determined when pk/2nd is above 3.

`fit_delay` searches the delay domain instead of unwrapping phase, so each
flagged gap only costs signal-to-noise; the `RFI_LINES` bands are 2 MHz wide
each and the added 465.3-466.7 MHz band is 1.4 MHz. It cannot bias the slope
by a multiple of 2π the way a gap-crossing unwrap does. The casm-bf-imaging
equivalent, `fit_delay_phase` in `casm_imaging/calibration/delay_fit.py`,
unwraps and runs `np.polyfit`, so it takes that bias across these gaps.

```python
k = int(np.argmax(np.where(params["low_quality"], 0.0, np.abs(params["delay_ns"]))))
vis_avg = fs["vis_stopped"][fs["time_mask"]].mean(axis=0)[:, k]
model = params["slope"][k] * fs["freq_mhz"] + params["intercept"][k]

fig, ax = plt.subplots(figsize=(8, 3.4))
good = fs["freq_mask"]
ax.plot(fs["freq_mhz"][good], np.angle(vis_avg[good]), ".", ms=1.5,
        color="tab:blue", label="measured")
ax.plot(fs["freq_mhz"][good], np.angle(np.exp(1j * model[good])), ".", ms=1.0,
        color="tab:red", alpha=0.6, label=f"fit, {params['delay_ns'][k]:+.1f} ns")
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Fringe-stopped phase (rad)")
ax.set_ylim(-np.pi, np.pi)
ax.set_title(fs["target_labels"][k])
ax.legend(loc="upper right", markerscale=6)
plt.show()
```

```{figure} ../_static/tutorials/delay/delay-phase-vs-freq.png
:alt: Fringe-stopped phase against frequency for one baseline, a red sawtooth of about twenty wraps overlaid on the blue measured points.

Output of the code above: antenna 9 by antenna 22, time-averaged over the eight
integrations. Flagged channels are dropped. Blue is the measured phase, red is
the fitted +225.3 ns line wrapped to ±π.
```

The sawtooth is the delay. One wrap per 1/τ in frequency, 4.4 MHz at 225 ns,
so counting stripes across the band gives the delay to a few percent before any
fit runs. Phase with no slope after fringe stopping means the antenna is
already aligned with the reference.

## What the numbers mean

**Cable length.** 1 ns is 0.30 m of free-space path, 0.198 m of coax at 0.66c
and 0.204 m of fibre at n = 1.47. The +225 ns on antenna 22 is about 45 m of
extra signal path against antenna 9, all of it inside the instrument.

**The delays group by SNAP board.** Against reference antenna 9 on SNAP 0: SNAP 1
sits at +221 ns mean (212 to 230), SNAP 3 at +127 ns (116 to 132), SNAP 2 at
+36 ns (22 to 48). The board term is the dominant one and the 17-26 ns spread
inside a board is per-antenna cabling. One sample of the 250 MHz ADC clock is
4.00 ns, so +221 ns is about 55 samples.

**A delay that jumps between days is a hardware event.** Whole-sample slips
appear as multiples of 4.00 ns and are what a SNAP reflash or `--do_sync`
produces: on 2026-08-19 the boards moved by -4.00, -8.0 and -12.06 ns and every
beam formed with the previous day's cal was decalibrated. Normal epoch-to-epoch
drift is 0.24 ns over two days against a 1.04 ns same-observation noise floor,
so anything above about 1 ns per board means re-solve before trusting coherent
beams (casm-wiki `weights-verification.md` check (f), `incidents.md` 2026-08-19).
Difference two cals from matched Sun-altitude windows to run that check; the
absolute delays on this page are not the comparison.

**How this feeds the SVD solve.** It does not. The solve is per channel
(`block_size=1`) and phase-only, so it absorbs a delay exactly: a delay is just
a smooth phase ramp across channels. There is no "extend the cal to the full
band" step in the weights build to feed either. `make_cal_and_weights` runs one
full-band per-channel solve; nothing extrapolates a delay across a gap. It sets
`masked_band_strategy="zero"`, but passes no `rfi_mask` to `fringe_stop` and
never calls `apply_rfi_mask`, so no channel is flagged and the strategy is
inert there: to zero flagged channels you must supply the mask yourself, as
this page shows. Delays would matter to the band only under
`masked_band_strategy="extrapolate"`, which the canonical recipe does not use.

**Where fitted delays go in the canonical pipeline.** `make_cal_and_weights`
never calls `casm_vis_analysis.delay.fit_delay`. It fits delays on the **solved
gain phase** with its own `recipe_diagnostics.delay_fit` (delay-domain search,
±300 ns at 0.02 ns, over 398-480 MHz minus `RFI_LINES`) and writes
`gain_delay_fits_<tag>.csv` plus the per-antenna delay column of the cal-diff
table. Those are diagnostics; no product byte depends on them. The visibility
delays fitted here are for triage and for the cross-epoch sample-slip check.

Next, solve the calibration itself and check it:
[plot SVD and rank-1 diagnostics](rank1-diagnostics.md).

## Provenance

Day 2026-08-23, Sun peak 19:56:00 UTC at altitude 63.99 deg. Window requested
19:46-20:06 UTC, returned 8 integrations, 19:48:00 to 20:04:02 UTC.
Data: `/mnt/nvme4/data/casm/visibilities_64ant/2026-08-23-19:18:14.dat.0`. The
reader also lists `2026-08-21-03:14:39.dat.52`, the tail of the previous
recording, which ends at 19:20:40 UTC and contributes no integration here.
Layout: `casm_antenna_layout_2026-08-07.csv`, matching this recording, 24 active
antennas. Figures rendered by `scripts/render_rfi_delay_tutorial.py`, which
executes the displayed blocks on this page and saves each figure in place of
`plt.show()`.
