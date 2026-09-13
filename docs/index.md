```{raw} html
<div class="eyebrow">OVRO · Scientific software · Documentation preview</div>
```

# CASM analysis software

```{raw} html
<div class="hero">
<p>Data access, visibility diagnostics and calibration. Package references and worked examples for the CASM analysis stack.</p>
</div>
<div class="package-grid">
<a class="package-card" href="packages/io.html"><small>01 / READ</small><strong>casm_io</strong><span>Visibility, voltage and filterbank data. Formats, subsets and antenna mappings.</span><em>Explore data access →</em></a>
<a class="package-card" href="packages/vis-analysis.html"><small>02 / UNDERSTAND</small><strong>casm_vis_analysis</strong><span>Fringe stopping, delay diagnostics, source geometry and scientific plots.</span><em>Explore diagnostics →</em></a>
<a class="package-card" href="packages/calibrator.html"><small>03 / CALIBRATE</small><strong>casm_calibrator</strong><span>SVD solutions, calibration products and the contracts between packages.</span><em>Explore calibration →</em></a>
</div>
```

## Start with a question

| I want to… | Start here |
|---|---|
| Read a bounded visibility interval | [Read visibilities](guides/read-visibilities.md) |
| Understand shapes, units and antenna IDs | [Data contracts](guides/contracts.md) |
| Compare a calibration across observing days | [Check a calibration](guides/check-calibration.md) |
| Reproduce the solar plotting style | [Solar waterfall](guides/solar-waterfall.md) |
| Find a function or command | [API and CLI index](reference.md) |
| Check what version these docs describe | [Sources and verification](sources.md) |

## Package boundaries

**casm_io** reads and maps data. **casm_vis_analysis** supplies geometry and
diagnostics. **casm_calibrator** solves and stores calibration products.
The canonical calibration-and-weights build belongs to `bf_weights_generator`,
outside this initial three-package preview.

CASM is being developed toward a 256-antenna FRB survey instrument at OVRO.
Solar observations, calibration checks and injection recovery support its
commissioning. These manuals explain software; current array state and
operational decisions remain in the [team wiki](knowledge.md).

See [sources and verification](sources.md) for the exact revisions and checks
behind this preview.

```{toctree}
:hidden:
:caption: Start here

getting-started
guides/contracts
knowledge
sources
```

```{toctree}
:hidden:
:caption: Packages

packages/io
packages/vis-analysis
packages/calibrator
```

```{toctree}
:hidden:
:caption: Workflows

guides/read-visibilities
guides/check-calibration
guides/solar-waterfall
```

```{toctree}
:hidden:
:caption: Reference

reference
packages/io-api
packages/vis-analysis-api
packages/calibrator-api
upstream
```
