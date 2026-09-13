# Developer documentation

Use this section to understand package interfaces, maintain the tutorials,
or investigate how a saved example was produced. Start with the
[tutorials](../tutorials.md) to learn the analysis workflow.

## Working on the software

`casm_io` owns data reading; `casm_vis_analysis` owns visibility diagnostics;
`casm_calibrator` owns gain solving. Reuse those modules when adding a workflow.
The [API reference](../reference.md) includes links to the recorded source code.
Read the owning repository's contributor instructions before changing it.

A change to an input shape, unit, default or output needs corresponding tests
and documentation. Small synthetic fixtures belong in unit tests; expensive
recorded-data comparisons run separately with an explicit resource budget.
The docs build must never acquire observations or deploy a product.

## Maintaining the documentation

Tutorials follow one task through short steps, with visible results early.
Reference pages carry signatures and exhaustive options. Implementation notes
hold hashes, historical limitations and reproducibility details. This separation
follows [Diátaxis](https://diataxis.fr/tutorials/): the beginner should be able
to finish the lesson without reading a source audit.

The scientific meaning of a figure stays in its caption. Its source paths and
hashes stay in the linked notes. Do not remove an important warning from the
step where it affects a user's result or could cause a destructive operation.

```{toctree}
:maxdepth: 1

../maintaining-docs
../sources
../machine-readable
io-example-notes
solar-example-notes
transit-example-notes
calibration-transfer-notes
imaging-notes
svd-notes
../guides/calibration-figures
weights-notes
folding-design
folding-notes
../upstream
```
