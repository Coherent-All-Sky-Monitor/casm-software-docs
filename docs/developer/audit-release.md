# Isolated software audit release

This candidate is developed in
`/home/casm/software/dev/worktrees/software-audit-20260913/` on the
`audit/maintainability-20260913` branches. No production checkout, editable
installation, service, or port-8070 site is switched by building this candidate.

## Verification and release boundaries

Run source tests against these worktrees, with explicit import paths. Do not
install editable worktrees into the environment used by running services.
Source commits and the documentation snapshot identify the reviewed combination;
historical scientific figures keep their original provenance.

The monitor candidate starts from the installed `worktree-m0-scaffold` branch,
not the implementation-free `main`. Uncommitted production UI, notebook, and
analysis changes were not copied into the audit branches. A later release must
reconcile those changes before switching environments.

## Janitor retired

The read-only service check on 2026-09-13 found `t3-janitor.service` enabled and
running since August 18, with PID 3004. `t3-janitor.timer` was not found. The
service loops hourly itself, using a 150 GB quota and a seven-day age limit.
The previous inference that an inactive timer meant cleanup was retired was
incorrect. Its process predates the September 9 patrol-glob source change;
the currently checked-out source is not evidence that the running process has
loaded that change.

The operator chose retirement on September 13. After 69 T3 tests passed,
`systemctl --user disable --now t3-janitor.service` stopped the production
janitor and removed its user-unit links. A subsequent check returned
`LoadState=not-found`, `ActiveState=inactive`, `SubState=dead` for both janitor
units. The plotter and collector remained enabled and running. No dump or log
was removed. The source unit remains recoverable from the original checkout
and Git history; do not re-enable its unsafe older deletion policy.

Candidate T3 revision `18b3d35` removes the deployment unit and leaves an inert
CLI that reports retirement, even with legacy flags. Programmatic `sweep()`
calls raise before any I/O. This source change is staged, not installed into
the shared Python environment.

The plotter's configured post-processing deletion remains.
Retained/failed beam dumps, raw voltage dumps and the event archive need storage
monitoring and separately approved cleanup; there is no replacement automatic
age/quota reaper in this release.

## Implementation scope

- Preserve visibility baseline identities and missing-data evidence through stitching.
- Validate calibration reference, mask dimensions, and axes before solving.
- Prevent deployment previews from recording live weights.
- Validate and order T3 dump segments before concatenation.
- Require explicit scheduler fill intent and preserve layout exclusions.
- Extract pure selection/analysis functions while preserving public imports.
- Correct declared runtime dependencies and verify isolated command imports.
- Generate tutorial figures from their displayed code or explicitly retain
  historical evidence where the source recording no longer exists.

## Checks and limits

Recorded bounded source checks, run against isolated imports:

| Component | Verification |
|---|---|
| I/O | 348 tests passed; three large-data cases excluded |
| Visibility analysis | 159 tests passed, including missing-row and baseline-identity regressions |
| Calibrator/recipe interfaces | 169 tests passed after the zero-signal fix |
| Weights generator | 179 tests passed; 12 skipped for an unavailable historical calibration NPZ |
| T2 | 423 tests passed |
| T3 | 69 tests passed, including segment continuity, event store and inert janitor |
| Monitor | 49 candidate/config/web tests passed; not a full live-service test |
| Imaging | 44 tests passed for reader delegation and imaging stages |
| Beam scheduler | 115 tests passed with isolated registry/FIFO boundaries |

Counts describe the selected suites, not coverage percentages or a proof of
scientific validity. The canonical recipe's cross-package checks also exercise
reader metadata, availability and frequency-mask contracts before release.

The adversarial integration review found that missing rows could produce good
calibration flags and that subset baselines could silently relabel gains. The
candidate now excludes unavailable integrations and rejects missing input
identities before solving. Calibrator also preserves masked-NaN behavior in
subband mode and historical package-root helper interception. Upstream
`fringe_stop` deliberately rejects subset triangles; this is an explicit
unsupported-input error, not a promise that every selected-input workflow works.
The final edge-case checks also found that phase-only normalization converted
zero visibilities into unit phasors. Revision `30b16ef` preserves zeros and
rejects signal-free solves; zero-data, diagonal-only, baseline-excluded and
threshold-zero regressions passed, including both canonical-recipe reproductions.

The [bounded tutorial checks](bounded-examples.md) execute five examples and
compare four regenerated PNGs with their retained figures. Voltage uses a small
selection from a real dump; rank-1, transit and all-sky examples use retained
scientific products. Redrawing an image is not rerunning its calibration or
imaging solve. The visibility and solar figures retain their earlier provenance.

The release check records eleven source repositories in
{download}`release-sources.json <../../release-sources.json>`
and verifies ten Python imports resolve inside the worktrees. The separate
`source-snapshot.json` pins the three generated API packages. Neither checker
is an end-to-end telescope test.

Wheel smoke tests build/install into a separate candidate environment, loading
shared dependencies read-only without processing their editable-install files.
This is an offline installation/import check, not a hermetic dependency solve.
Console entry points are imported, not run as acquisition or deployment jobs.

The corr1 Hella build completed in a fresh audit output directory. Its existing
compiler warnings remain; no GPU search/replay or corr2 compilation was run.
No full calibration, weight generation, fold, observing run or live injection
was performed for this audit. Production rollout still requires reconciliation
of uncommitted operational changes and an operator-reviewed deployment plan.
