# Tutorials

The tutorials follow the order of a calibration campaign: read the data, remove
the quiet-sky background, fringe-stop toward the Sun, solve the calibration, build
and deploy beam weights, then check the result on another day and on Cyg A. Each
page runs a short piece of Python against an existing CASM observation with the
same modules the analysis notebooks use.

## Read the data

- [Read visibilities and plot spectra](guides/read-visibilities.md): open a
  recording, select times and channels, compare antennas.
- [Read a voltage dump](guides/read-voltages.md): inspect the raw signal and
  correlate two inputs in software.
- [Convert a beam dump to a filterbank](guides/beamdump-to-filterbank.md):
  the prerequisite for folding and dynamic spectra.

## Calibrate on the Sun

- [Build an off-source static template](guides/static-template.md): choose the
  quiet window and build the template the solve subtracts.
- [Solar transit phase](guides/solar-phase.md): read the phase pattern before and
  after fringe stopping.
- [Mask RFI and fit per-antenna delays](guides/rfi-and-delay.md): flag the
  465 MHz band, measure coherence, fit the sawtooth.
- [Solve a solar calibration and plot rank-1 against frequency](guides/rank1-diagnostics.md):
  the SVD solve and how to read its diagnostics.
- [Generate calibration and beam weights](guides/generate-weights.md): the
  canonical driver from solve to the 512-beam grid.
- [Review and deploy weights](guides/deploy-weights.md): staging, dry runs and
  the human-only upload.

## Check the calibration

- [Check a calibration on another day](guides/cross-day-phase.md): apply the
  gains to a later transit and measure residual phase.
- [Beamform toward Cyg A](guides/check-calibration.md): the referee that
  adjudicates calibration variants.
- [Image the sky](guides/image-visibilities.md): a source-centred dirty image and
  its PSF.

## Search products

- [Solar waterfall](guides/solar-waterfall.md): dynamic spectrum of a beam.
- [Find a pulsar](guides/fold-b0329.md): fold a B0329+54 recording.
- [Follow an injection](guides/injection-recovery.md): trace a test pulse through
  T2/T3.

```{toctree}
:hidden:
:maxdepth: 1

guides/read-visibilities
guides/read-voltages
guides/beamdump-to-filterbank
guides/static-template
guides/solar-phase
guides/rfi-and-delay
guides/rank1-diagnostics
guides/generate-weights
guides/deploy-weights
guides/cross-day-phase
guides/check-calibration
guides/image-visibilities
guides/solar-waterfall
guides/fold-b0329
guides/injection-recovery
```
