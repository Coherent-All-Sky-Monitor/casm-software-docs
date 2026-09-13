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

- [Visibilities and antenna spectra](guides/read-visibilities.md): read an
  observation, select times and channels, and plot auto- and cross-correlations.
- [Voltage dumps](guides/read-voltages.md): inspect recorded antenna signals.
- [Solar phase](guides/solar-phase.md) and [dynamic spectra](guides/solar-waterfall.md):
  follow the Sun in baseline phase and beam power.
- [Cyg A transit](guides/check-calibration.md): check the response of a fixed beam.
- [SVD diagnostics](guides/rank1-diagnostics.md),
  [sky imaging](guides/image-visibilities.md) and
  [pulsar folding](guides/fold-b0329.md): work with saved scientific results.
- [Injection recovery](guides/injection-recovery.md): follow a test pulse through
  T2/T3, inspect its saved plots and find the event products.

```{figure} _static/tutorials/solar/solar-waterfall.webp
:alt: Solar observing dynamic spectrum with frequency bandpass and channel light curves.

Solar observing data: changes in received power across time and frequency.
[Plot a dynamic spectrum](guides/solar-waterfall.md).
```

## Calibration procedures

[Generate calibration and beam weights](guides/generate-weights.md), then
[review and deploy the product](guides/deploy-weights.md). Deployment requires
human approval.

## Software reference

**casm_io** reads and maps data. **casm_vis_analysis** supplies geometry and
diagnostics. **casm_calibrator** solves and stores calibration products.
The calibration-and-weights build belongs to `bf_weights_generator` and imaging
to `casm-bf-imaging`. Their workflows are covered here; the initial API inventory
covers the three packages above.
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
:caption: How-to guides

guides/generate-weights
guides/deploy-weights
```

```{toctree}
:hidden:
:caption: Development

developer/index
```
