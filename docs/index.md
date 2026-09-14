---
myst:
  html_meta:
    description: "CASM data access, calibration and imaging tutorials with scientific figures and versioned API references."
---

# CASM analysis software

Python tools for reading CASM observations, plotting visibilities and calibrating
the array at Owens Valley Radio Observatory.

New to these modules? Start with [Getting started](getting-started.md), then
follow the [tutorials](tutorials.md) in order.

## Tutorials

Read the data:

- [Read visibilities and plot spectra](guides/read-visibilities.md): open a
  recording, select times and channels, compare antennas.
- [Read a voltage dump](guides/read-voltages.md): inspect the raw signal.
- [Convert a beam dump to a filterbank](guides/beamdump-to-filterbank.md).

Calibrate on the Sun:

- [Build an off-source static template](guides/static-template.md).
- [Solar transit phase](guides/solar-phase.md): phase before and after
  fringe stopping.
- [Mask RFI and fit per-antenna delays](guides/rfi-and-delay.md).
- [Solve a solar calibration and plot rank-1 against frequency](guides/rank1-diagnostics.md).
- [Generate calibration and beam weights](guides/generate-weights.md) and
  [review and deploy them](guides/deploy-weights.md).

Check the calibration:

- [Check a calibration on another day](guides/cross-day-phase.md): residual
  baseline phase.
- [Beamform toward Cyg A and check a calibration](guides/check-calibration.md).
- [Image the sky](guides/image-visibilities.md): a source-centred dirty image
  and its PSF.

Search products:

- [Solar waterfall](guides/solar-waterfall.md) and
  [pulsar folding](guides/fold-b0329.md).
- [Injection recovery](guides/injection-recovery.md): follow a test pulse through
  T2/T3, inspect its saved plots and find the event products.

```{figure} _static/tutorials/solar/solar-waterfall.webp
:alt: Solar observing dynamic spectrum with frequency bandpass and channel light curves.

Solar observing data: changes in received power across time and frequency.
[Plot a dynamic spectrum](guides/solar-waterfall.md).
```

## Calibration procedures

The calibration campaign runs in the order the [tutorials](tutorials.md) are
listed: static template, fringe stop, solve, weights, deploy, then the
cross-day and Cyg A checks. Deployment requires human approval.

## Software reference

**casm_io** reads and maps data. **casm_vis_analysis** supplies geometry and
diagnostics. **casm_calibrator** solves and stores calibration products.
The calibration-and-weights build belongs to `bf_weights_generator` and imaging
to `casm-bf-imaging`. Their workflows are covered here.
[casm_t2 and casm_t3](packages/t2-t3.md) handle candidate selection and event
processing, with injection recovery providing an end-to-end search check.

CASM is being developed toward a 256-antenna FRB survey instrument at OVRO.
Solar observations, calibration checks and injection recovery support its
commissioning. These manuals explain software; current array state and
operational decisions remain in the [team wiki](knowledge.md).

Function signatures and source-code links are in the [API reference](reference.md).
Build instructions, versioning and example details are in the
[developer documentation](developer/index.md).

```{toctree}
:hidden:
:caption: Start here

getting-started
tutorials
knowledge
```

```{toctree}
:hidden:
:caption: Reference

guides/contracts
packages/io
packages/vis-analysis
packages/calibrator
packages/t2-t3
reference
packages/io-api
packages/vis-analysis-api
packages/calibrator-api
```

```{toctree}
:hidden:
:caption: Development

developer/index
```
