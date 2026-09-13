# Tutorials

Start with a spectrum, then work toward a source transit. Each tutorial combines
short Python examples with plots from existing CASM observations.

## First observations

- [Read visibilities and plot spectra](guides/read-visibilities.md): import the
  modules, open a recording, select times and channels, and compare antennas.
- [Read a voltage dump](guides/read-voltages.md): inspect a short piece of the
  recorded signal before averaging it into power.

## The Sun and the array

- [Solar transit phase](guides/solar-phase.md): interpret the red/blue phase
  pattern before and after fringe stopping.
- [Solar waterfall](guides/solar-waterfall.md): plot intensity against frequency
  and time, alongside spectra and light curves.
- [Cyg A transit](guides/check-calibration.md): watch a source cross a fixed beam.
- [SVD diagnostics](guides/rank1-diagnostics.md): inspect a saved calibration solve.

## Further analysis

- [Image the sky](guides/image-visibilities.md): make a source-centred dirty image.
- [Find a pulsar](guides/fold-b0329.md): understand a folded B0329+54 recording.

```{toctree}
:hidden:
:maxdepth: 1

guides/read-visibilities
guides/read-voltages
guides/solar-phase
guides/solar-waterfall
guides/check-calibration
guides/rank1-diagnostics
guides/image-visibilities
guides/fold-b0329
```
