# Beamform toward Cyg A and check a calibration

A solar calibration is solved on one source and used on the whole sky. The
check that it transferred is a bright point source at night: point a fixed
beam at Cyg A's meridian crossing, let the sky rotate the source through it,
and see whether the power rises and falls at the predicted time while an
off-source control does not. This is the referee that decides between
calibration variants; the solve's rank-1 ratio is not
(casm-wiki `rank1-metric-caveat.md`).

## Pick a calibration and a window in the same instrument epoch

Any F-engine `--do_sync` or reflash voids a calibration, so the Cyg A window
and the solve have to sit on the same side of every sync. The example below
uses the August 23 solar calibration and the Cyg A transit of the following
night, with no sync in between (casm-wiki `weights-verification.md`).

```text
cal_aug23_exact512_CAL0823N.h5          Sun, 2026-08-23 20:41-21:41 UTC, ref ant 9, 16 antennas
static_aug23_exact512_CAL0823N.npz      night static, 2026-08-24 03:00-03:30 UTC
weights_aug23_exact512_CAL0823N_16ant_512_int8.h5   the 512-beam grid built from that cal
```

## Predict the crossing with the exact array-factor tool

Take the pointing and the predicted peak time from the exact array-factor
response of the deployed grid, never from an analytic beam ellipse: the
ellipse mispredicted on-sun peaks by 15-45 minutes
(casm-wiki `incidents.md`, 2026-08-20). `casm-bf-source-transit --exact`
prints the same table from the shell.

```python
from bf_weights_generator.plot_transit import array_factor_response, exact_transit_report

CAL_DIR = "/mnt/nvme5/vishnu/cal_build_20260824"
WEIGHTS = f"{CAL_DIR}/weights_aug23_exact512_CAL0823N_16ant_512_int8.h5"

response = array_factor_response(
    WEIGHTS, "cyg-a", date="2026-08-24", time_tz="UTC",
    time_start="03:00", time_end="08:00", dt_minutes=0.5,
)
# Each row is one grid beam; take the one the source crosses at its highest
# point. peak_alt/peak_az are the SOURCE alt/az at that predicted peak time,
# not the stored centre of the grid beam.
transit = max(exact_transit_report(response, threshold=0.0),
              key=lambda row: row["peak_alt"])
alt_deg, az_deg = transit["peak_alt"], transit["peak_az"]
predicted_unix = transit["peak_time"].unix
print(transit["peak_time"].utc.iso, f"alt {alt_deg:.3f} az {az_deg:.3f}")
```

Prints `2026-08-24 05:43:02.609 alt 86.423 az 1.232`.

`exact_transit_report` fills `peak_alt`/`peak_az` from the source track at the
predicted peak time (`plot_transit.py:503-505`), so the stationary beam below
is pointed at the source position, not at the grid beam centre. That is a valid
stationary-beam test of the calibration: the beam sits where the source will
be. To check a **deployed** grid beam instead, read that beam's centre out of
the weights file and point there; the source position and the beam centre
differ by up to half a beam spacing.

## Read the transit and remove the static background

Read the full correlator triangle. `beam_power_vs_time` needs it: it rebuilds
baseline indices from the triangle size. `fringe_stop` accepts a pre-filtered
`ref=`/`targets=` read (`fringe_stop.py:255-259`) and rejects only input
subtriangles, `inputs=` and `nsig_subset` (L277-283). Two hours centred on
the crossing covers the response, which is about 90 minutes wide at half
maximum.

The raw cross-baseline sum is dominated by a static instrumental pedestal
larger than Cyg A. Subtract the night static recorded with the same
calibration, and mask the four known RFI lines before averaging in frequency.

```python
import numpy as np
from bf_weights_generator.snap_weights import load_calibration_weights
from casm_io.correlator import AntennaMapping, read_visibilities
from casm_vis_analysis.offsource import load_static_visibility, subtract_static_visibility

LAYOUT = "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
ANTENNAS = [9, 10, 15, 19, 22, 23, 24, 26, 30, 32, 36, 38, 40, 42, 44, 45]

data = read_visibilities(
    data_root="/mnt/nvme4/data/casm",
    time_start="2026-08-24 04:43:00", time_end="2026-08-24 06:43:00",
    time_tz="UTC", workers=1, verbose=False,
)
print(data.vis.shape, data.metadata["files"])

static = load_static_visibility(f"{CAL_DIR}/static_aug23_exact512_CAL0823N.npz")
clean = subtract_static_visibility(data, static["static_vis"])
freq_mhz = np.asarray(data.freq_mhz)
flagged = np.zeros(freq_mhz.size, dtype=bool)          # True = drop the channel
for lo, hi in [(462.0, 464.0), (450.0, 452.0), (436.5, 438.5), (400.0, 402.0)]:
    flagged |= (freq_mhz > lo) & (freq_mhz < hi)

cal = load_calibration_weights(f"{CAL_DIR}/cal_aug23_exact512_CAL0823N.h5")
# drop channels the solve failed (weight 0 would read as phase 0)
flagged |= ~cal.flags[::-1]                # cal ascending, read descending
clean["freq_mask"] = flagged

ant = AntennaMapping.load(LAYOUT)
ant = ant.with_inactive([a for a in ant.active_antennas() if a not in ANTENNAS])
```

Prints `(52, 3072, 8256) ['2026-08-24-01:54:29.dat.2', '2026-08-24-01:54:29.dat.3']`.
The read holds the whole triangle in memory: 10.5 GB for these 52
integrations, and about 29 GB peak while the reader materialises each file
and the static subtraction makes its copy. Budget for that before widening
the window.

Use the layout the calibration was built with, not `antenna_layouts/current`,
and the same 16 antennas the solve used.

## Apply the calibration and form the beam

`load_calibration_weights` returns `ant_ids` exactly as stored in the HDF5,
which are **1-indexed antenna numbers**, while correlator inputs are
`packet_idx = antenna - 1`. `beam_power_vs_time` looks each active antenna up
by identity (`cal_ant_ids.index(antenna_id)`) instead of using `ant_ids` as
row indices, so the off-by-one cannot happen here. Hand-rolled beam code that
indexes visibilities with `ant_ids` applies each antenna's calibration to its
neighbour's signal: the transit still appears, with a fake 7 degree east
pointing offset and frequency-dependent transit times
(casm-wiki `conventions.md`).

The off-source control is 25 degrees **below** the source in altitude, the
same null the weights driver uses. An azimuth offset is useless this close to
zenith: 25 degrees of azimuth at altitude 86 moves the beam 1.7 degrees, well
inside it.

```python
from datetime import timezone

import matplotlib.pyplot as plt
from bf_weights_generator.snap_weights import load_calibration_weights
from casm_vis_analysis.beam_power import beam_power_vs_time, plot_beam_power

cal = load_calibration_weights(f"{CAL_DIR}/cal_aug23_exact512_CAL0823N.h5")
result = beam_power_vs_time(
    clean, ant,
    sources=[("Cyg A", alt_deg, az_deg), ("off-source", alt_deg - 25.0, az_deg)],
    cal_weights=cal, freq_band_mhz=(398.0, 480.0), sign=-1,
)

time_unix = result["time_unix"]
on, off = result["power"]["Cyg A"], result["power"]["off-source"]
# Half maximum of the peak: static subtraction puts the off-source level at 0,
# so no baseline term is needed. Same rule as exact_transit_report.
above = np.flatnonzero(on >= 0.5 * on.max())
midpoint = 0.5 * (time_unix[above[0]] + time_unix[above[-1]])
print(f"channels {result['n_chan_used']}, "
      f"midpoint {(midpoint - predicted_unix) / 60:+.1f} min from prediction, "
      f"width {(time_unix[above[-1]] - time_unix[above[0]]) / 60:.1f} min, "
      f"on/off {on[above].mean() / np.abs(off).mean():.2f}")

figure = plot_beam_power(result, time_tz="UTC")
axis = figure.axes[0]
axis.axvline(transit["peak_time"].to_datetime(timezone=timezone.utc),
             color="k", ls="--", lw=0.9, label="predicted peak")
axis.set_xlabel("Time (UTC, 2026-08-24)")
axis.legend(fontsize=9, loc="upper left")
plt.show()
```

Prints `channels 2425, midpoint +2.8 min from prediction, width 91.6 min, on/off 4.05`.

```{figure} ../_static/tutorials/transit/cyga-beam-power.png
:alt: Cyg A stationary-beam power rising and falling across two hours, with an off-source control near zero and a dashed line at the predicted peak.

Output of the code above. Fixed beam at altitude 86.423, azimuth 1.232,
2425 channels over 398-480 MHz, 52 integrations on 2026-08-24,
04:43:59-06:40:48 UTC, August 23 solar calibration with its night static
subtracted.
```

## What to look for

The on-source curve rises and falls once, its half-maximum midpoint lands on
the predicted crossing, and the control stays near zero. Here the midpoint is
05:45:50 UTC against a predicted 05:43:03, and the mean in-band power over the
half-maximum window is 4.05 times the mean off-source level. The control keeps
a residual drift of about 0.5e6, a third of the on-source peak, so read the
contrast rather than an absolute floor.

The 05:00 spike
appears at full height in both pointings, which makes it interference rather
than a beam response. The slow off-source wander sets the scale a shifted or
broadened on-source curve has to be judged against; with one pointing only, a
drift that size reads as a real response.

Quote the cross-only number. The visibility-domain achromaticity check on
CAL0819 measured a per-channel half-max midpoint scatter of 0.95 minutes and
a chromatic trend of +0.23 minutes across 390-484 MHz, a tenth of one
integration; the same run with autocorrelations included gives -2.68 minutes
and fails (casm-wiki `weights-verification.md`, check d).
`beam_power_vs_time` returns cross-only power already, and returns it
averaged over the band, so the per-channel version of that scatter cannot be
computed from `result`: it needs the waterfall script named on that wiki page.

This is the measurement that adjudicates calibration variants: ranking cals by
rank-1 has picked the worse one on sky (wiki `rank1-metric-caveat.md`). Re-run
this page with each candidate cal on identical data, antennas, masks and
control, and compare. The weights driver's own beam check on this build, a tracking beam
rather than a stationary one, scored the new cal 0.0646 against 0.0674 for
the previous cal and 0.0175 for the null, so it preferred the older
calibration.

One thing a single Cyg A check does not settle: with an antenna position
error the best cal depends on the target direction, so a Cyg A referee ranks
calibrations for Cyg A's direction only (casm-wiki `rank1-metric-caveat.md`).

Passing the string `"cyg_a"` instead of the `(label, alt, az)` tuple tracks
the source and measures something else: a flat coherence level across the
window, 1.48e6 in these units, with no transit shape to time.

## Historical reference

```{figure} ../_static/tutorials/transit/cyga_stationary_beam_20260805.png
:alt: Cyg A stationary-beam waterfall above an orange power curve peaking shortly after transit.

The same measurement on 2026-08-05 with 18 antennas, an August 2 calibration
and a 5-hour window, showing the per-channel waterfall this page's band
average hides. Details in the
[transit example notes](../developer/transit-example-notes.md).
```

## Next

[Cross-day calibration checks](../developer/calibration-transfer-notes.md)
compare baseline phase residuals between days with the same saved weights.
Sky imaging is a separate [tutorial](image-visibilities.md).

## Provenance

Data: `/mnt/nvme4/data/casm/visibilities_64ant`, observation
`2026-08-24-01:54:29`, files `.dat.2` and `.dat.3`, 04:43-06:43 UTC on
2026-08-24 (52 integrations returned, 04:43:59-06:40:48 UTC).
Calibration, static and beam grid: `/mnt/nvme5/vishnu/cal_build_20260824`.
Layout: `casm_antenna_layout_2026-08-07.csv`, matching that calibration.
Figure rendered by `scripts/render_cyga_tutorial.py`, which executes the
displayed blocks in this page and saves the figure in place of `plt.show()`.
