# Sources and verification

This preview uses explicitly inspected source checkouts. Git revisions identify the baseline; SHA-256 hashes identify the actual files read. Untracked source files are excluded.

| Package | Baseline revision | Tracked working-tree changes |
|---|---|---|
| casm_io | `73279e93fb41` | 0 |
| casm_vis_analysis | `9ec630267fb8` | 3 |
| casm_calibrator | `fe5a5fbfb44d` | 0 |

## Verification boundaries

- API signatures and command entry points are extracted from tracked source.
- Existing manuals are preserved as downloads; curated pages identify known discrepancies.
- Example syntax and selected installed signatures are checked separately. Real-data examples remain illustrative unless explicitly marked otherwise.
- These documentation checks do not validate telescope state, scientific sensitivity, or an operational recipe.
- Dirty notebook changes in a source checkout do not become undocumented defaults. File hashes in the snapshot identify exactly what was consumed.

## Reproducing the snapshot

The repository contains `sources.json` (the allowlist and selected modules), `source-snapshot.json` (revisions and file hashes), and `scripts/snapshot_sources.py`. Refresh explicitly, review the diff, then rebuild. The committed pages and downloads can build without source checkouts.


## Version policy

Documentation snapshot: `49b7cd30e5ea5d94`. Coverage starts with this preview; no historical-version backfill is planned. Package version strings alone are insufficient to identify these checkouts, so revision plus file hashes are authoritative for this documentation.

Run `python scripts/snapshot_sources.py --source-root /home/casm/software/dev --check` before refreshing to detect source drift. Future releases should pair a reviewed software revision with a documentation snapshot. Snapshot generation does not edit source repositories.

Source instruction updates may be committed locally before publication. GitHub baseline links for those commits become available after the owner pushes; the built-in source views work from the recorded copies now.
