# Sources and verification

This preview uses explicitly inspected source checkouts. Git revisions identify the baseline; SHA-256 hashes identify the actual files read. Untracked source files are excluded.

| Package | Baseline revision | Tracked working-tree changes |
|---|---|---|
| casm_io | `22ef826d9f2b` | 0 |
| casm_vis_analysis | `5039eb4714b5` | 3 |
| casm_calibrator | `8b5fcf5b089d` | 0 |

## Verification boundaries

- API signatures and command entry points are extracted from tracked source.
- Existing manuals are preserved as downloads; curated pages identify known discrepancies.
- Example syntax and selected installed signatures are checked separately. Real-data examples remain illustrative unless explicitly marked otherwise.
- These documentation checks do not validate telescope state, scientific sensitivity, or an operational recipe.
- Dirty notebook changes in a source checkout do not become undocumented defaults. File hashes in the snapshot identify exactly what was consumed.

## Reproducing the snapshot

The repository contains `sources.json` (the allowlist and selected modules), `source-snapshot.json` (revisions and file hashes), and `scripts/snapshot_sources.py`. Refresh explicitly, review the diff, then rebuild. The committed pages and downloads can build without source checkouts.


## Version policy

Documentation snapshot: `3ee877e0a4612dd1`. Coverage starts with this preview; no historical-version backfill is planned. Package version strings alone are insufficient to identify these checkouts, so revision plus file hashes are authoritative for this documentation.

Run `python scripts/snapshot_sources.py --source-root /home/casm/software/dev --check` before refreshing to detect source drift. Future releases should pair a reviewed software revision with a documentation snapshot; this preview does not tag or alter source repositories.
