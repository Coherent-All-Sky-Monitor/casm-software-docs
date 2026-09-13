---
myst:
  html_meta:
    description: "CASM data access, calibration and imaging tutorials with scientific figures and versioned API references."
---

```{raw} html
<div class="eyebrow">OVRO · Scientific software · Documentation preview</div>
```

# CASM analysis software

```{raw} html
<div class="hero">
<p>Read an observation, make your first plots, and learn how to check the array. Worked examples from CASM at OVRO.</p>
</div>
<div class="package-grid">
<a class="package-card" href="guides/read-visibilities.html"><small>01 / FIRST PLOTS</small><strong>Read an observation</strong><span>Load visibilities, slice time and frequency, and plot auto- and cross-correlations.</span><em>Start the tutorial →</em></a>
<a class="package-card" href="guides/solar-waterfall.html"><small>02 / SOLAR SCIENCE</small><strong>See the Sun</strong><span>Follow solar phase and explore a dynamic spectrum with bandpass and light curves.</span><em>Plot a solar waterfall →</em></a>
<a class="package-card" href="guides/check-calibration.html"><small>03 / BEAM CHECK</small><strong>Watch a transit</strong><span>See power rise and fall as Cyg A crosses a stationary beam.</span><em>Explore the transit →</em></a>
</div>
```

New to these modules? Start with [Getting started](getting-started.md), then
follow the [tutorials](tutorials.md) in order.

## Find a task

| I want to… | Start here |
|---|---|
| Read a bounded visibility interval | [Read visibilities](guides/read-visibilities.md) |
| Understand array dimensions and labels | [Shapes, units and antenna IDs](guides/contracts.md) |
| Open a saved voltage dump | [Read voltages](guides/read-voltages.md) |
| Understand solar red/blue phase plots | [Solar phase](guides/solar-phase.md) |
| Compare a calibration across observing days | [Check a calibration](guides/check-calibration.md) |
| Generate calibration and beamforming weights | [Build weights](guides/generate-weights.md) |
| Review and deploy a paired weights product | [Deploy weights](guides/deploy-weights.md) |
| Interpret SVD rank-1 plots | [Rank-1 diagnostics](guides/rank1-diagnostics.md) |
| Form an image from visibilities | [Visibility imaging](guides/image-visibilities.md) |
| Fold a B0329+54 observation | [B0329+54 tutorial](guides/fold-b0329.md) |
| Reproduce the solar plotting style | [Solar waterfall](guides/solar-waterfall.md) |
| Find a function or command | [API and CLI index](reference.md) |
| Check what version these docs describe | [Sources and verification](sources.md) |

## Software reference

**casm_io** reads and maps data. **casm_vis_analysis** supplies geometry and
diagnostics. **casm_calibrator** solves and stores calibration products.
The calibration-and-weights build belongs to `bf_weights_generator` and imaging
to `casm-bf-imaging`. Their workflows are covered here; the initial API inventory
covers the three packages above.

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
