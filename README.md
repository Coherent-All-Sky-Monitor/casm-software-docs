# CASM software documentation

A local, searchable Sphinx preview for casm_io, casm_vis_analysis and
casm_calibrator. Source repositories are read-only inputs. No telescope
packages are imported by the reference generator.

## Build and preview

Use the team's existing environment:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
python -m pip install -r requirements-docs.txt
python -m sphinx -W --keep-going -b html docs _build/html
python scripts/check_site.py
python scripts/check_exports.py
python -m http.server 8070 --bind 127.0.0.1 --directory _build/html
```

Open http://127.0.0.1:8070. From your workstation:

```bash
ssh -L 8070:127.0.0.1:8070 casm-corr1
```

Browser verification is optional and runs headlessly on the host:

```bash
python -m pip install -r requirements-preview.txt
python -m playwright install chromium
python scripts/check_browser.py
```

It checks navigation, search and mobile layout and saves screenshots under
`_build/screenshots/`. It requires the local preview server to be running.

The preview is a static documentation site. It does not replace or restart
the monitoring services, contact hardware, or change any data products.

## Refresh the reference snapshot

```bash
python scripts/snapshot_sources.py --source-root /home/casm/software/dev
```

Use the same command with `--check` to detect drift without changing the
snapshot. Coverage begins now; historical releases are not backfilled. The
snapshot records package version strings, git revisions, and exact file hashes.

This reads only the three allowlisted repositories in `sources.json`.
It extracts tracked Python definitions and CLI metadata, copies existing
tracked Markdown manuals as downloads, and records source hashes and git
revisions in `source-snapshot.json`. Existing dirty source files are identified;
untracked scientific files are excluded. Generated documentation and snapshot
metadata live here, so the site can subsequently build without source checkouts.

Review changes before committing. Existing manuals can carry historical claims;
their downloads are labelled as source material, not silently promoted into
current operational guidance. Verify examples separately against the appropriate
software environment. Read local source instructions before documenting another
package. Add new repositories only after maintainership/scope is confirmed.

## Editing

See `docs/maintaining-docs.md` for the code-change and documentation-release
workflow. Cross-repository CI and automatic publication are planned, not enabled.
Each build generates Markdown pages and `llms.txt` with `sphinx_llm.txt`;
no model-generated summaries or scientific notebook execution is enabled.
Sphinx source views read the recorded Python files in `docs/_code`, without
importing the scientific packages.

- `docs/packages/`: curated package guides and generated `*-api.md` references.
- `docs/guides/`: task guides with explicit contracts and limitations.
- `docs/_downloads/`: copied upstream manuals for this source snapshot.
- `docs/_code/`: recorded Python source used by Sphinx's source-code viewer.
- `docs/_static/tutorials/`: unchanged historical figures with provenance in the guides.
- `docs/_static/casm.css`: visual styling over Furo.
- `scripts/`: source extraction and local HTML integrity checks.

Do not edit a scientific repository to repair its documentation through this
project. Record discrepancies with source locations and propose upstream fixes
separately. Do not publish or push without the operator's instruction.
