# See the Sun in baseline phase

A phase waterfall shows how the relative signal phase between two antennas
changes with time and frequency. Compare the measured phase with the geometric
prediction for the Sun, then remove that predicted motion by fringe stopping.

After [reading your first visibilities](read-visibilities.md), select a daytime
window and its dated layout. This uses the same ten-minute recording as the
first tutorial, with antenna 9 as the reference.

```python
from casm_io.correlator import AntennaMapping, read_visibilities

ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-19_bf17.csv"
)
target_ids = sorted(a for a in ant.active_antennas() if a != 9)
data = read_visibilities(
    data_dir="/mnt/nvme4/data/casm/visibilities_64ant",
    time_start="2026-08-19 18:04:00", time_end="2026-08-19 18:14:00",
    time_tz="UTC", ref=ant.packet_index(9),
    targets=[ant.packet_index(a) for a in target_ids],
    freq_order="descending", workers=1,
)
print(data.vis.shape)  # time, frequency, reference-to-target baseline
```

This reads only reference-to-target cross-correlations, in the order expected
by fringe stopping. Do not substitute the two-input triangle from the first
tutorial. Antenna 9 must be active in your selected layout.

```python
import matplotlib.pyplot as plt
from casm_vis_analysis.fringe_stop import fringe_stop
from casm_vis_analysis.plotting.fringe_diag import plot_fringe_diagnostic

fs = fringe_stop(data, ant, ref_ant=9, source="sun", sign=-1)
figures = plot_fringe_diagnostic(
    panels=[
        ("Raw phase", fs["vis"]),
        ("Geometric", fs["geometric_phase"]),
        ("Fringe-stopped", fs["vis_stopped"]),
    ],
    time_unix=fs["time_unix"],
    freq_mhz=fs["freq_mhz"],
    target_labels=fs["target_labels"],
    target_snaps=[ant.snap_adc(a)[0] for a in fs["target_aids"]],
    ref_snap=ant.snap_adc(9)[0],
    freq_mask=fs["freq_mask"],
    time_tz="America/Los_Angeles",
)
plt.show()
```

The existing renderer uses **RdBu** with phase fixed to −π…+π radians. Here is
the same three-stage view from a saved solar calibration notebook:

```{figure} ../_static/tutorials/solar/solar-phase.png
:alt: Four solar baseline rows showing raw phase, geometric phase, and fringe-stopped phase in red and blue.

August 19, 2026 solar observation. Each row is a baseline from reference
antenna 9 to an input on SNAP 2; each column is a processing stage.
The saved example also subtracts a night-time background before these stages;
the short example above starts from the recorded visibilities.
```

Read across one row. Sloping bands in **Raw phase** become more nearly horizontal
after the Sun's geometric motion is removed. Remaining frequency bands can carry
instrumental delay; fringe stopping alone does not flatten that delay.

Red and blue show phase, not signal strength or “bad” and “good.” The endpoints
−π and +π represent the same phase, so an abrupt red/blue boundary can be a wrap.
Check amplitude or coherence before interpreting noisy phase. A white region can
be masked data or phase near zero, depending on the surrounding pattern.

The saved notebook relabels its time axis to local clock time. The plotting
primitive above uses elapsed hours, with the dated observation interval in its
header. Its output is grouped by SNAP pair, so several figures may be returned.

Next, compare [calibration residuals and an independent source](check-calibration.md).

[Source, data, and verification notes](../developer/solar-example-notes.md).
