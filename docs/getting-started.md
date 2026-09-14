# Getting started

Start with a short visibility recording and make your first spectrum. Then
follow a baseline through a solar transit, or open a saved voltage dump.
The tutorials use the same Python modules as the team's analysis notebooks.

## Open a Python session or notebook

New runs use `/home/casm/software/dev/antenna_layouts/current`; historical
figures name the dated CSV they used. `functional` describes wiring;
`include_in_beamforming` selects participation in weight generation. Neither
proves which weights are currently deployed. Keep the resolved layout with
each calibration product.

Do not refresh the layout as part of running a tutorial. `casm-layout apply`
preserves reviewed membership for unchanged feed identities; new, changed, or
ambiguous feeds remain excluded pending review. Tutorial reads do not need a
layout refresh. Check which checkout your environment resolves before relying
on this behaviour:

```
python -c "import bf_weights_generator, casm_calibrator; print(bf_weights_generator.__file__); print(casm_calibrator.__file__)"
```

A path under `software/dev/worktrees/` is the audit candidate; a path under
`software/dev/<repo>` is the main checkout.

On the CASM host, the software is already installed in the shared environment:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
cd /home/casm
python
```

For a notebook, select the Python interpreter from this environment. Work
outside `software/dev` so repository directory names do not shadow the
installed packages.

Import the functions you need, rather than copying a whole analysis script:

```python
from casm_io.correlator import read_visibilities, AntennaMapping
from casm_vis_analysis import run_autocorr, run_waterfall
```

`casm_io` reads the data. `casm_vis_analysis` supplies plotting and analysis
routines. Later, `casm_calibrator` solves antenna gains and
`bf_weights_generator` builds the beamforming weights.

## Your first tutorials

1. [Read visibilities and plot spectra](guides/read-visibilities.md): choose a
   time interval, slice frequency channels, and plot auto- and cross-correlations.
2. [Read a voltage dump](guides/read-voltages.md): open a saved recording and
   select a small time interval without loading the whole file.
3. [Follow solar phase through a transit](guides/solar-phase.md): read the
   red/blue phase pattern and see what fringe stopping changes.
4. [Plot a solar waterfall](guides/solar-waterfall.md): display intensity versus
   time and frequency, with a bandpass and light curves.
5. [Watch Cyg A cross a beam](guides/check-calibration.md): interpret the rise
   and fall of visibility-derived beam power.

Each page shows an existing observation and a short example. Observation files
are on the CASM machines; this site does not distribute the raw recordings.
Dataset locations and implementation details are linked separately.

Keep [array shapes, units and antenna IDs](guides/contracts.md) nearby as a
reference. For development, start with the [developer guide](developer/index.md).
