# Reading these docs with an agent

The human pages and machine-readable pages come from the same Sphinx sources.
The build publishes `llms.txt`, `llms-full.txt`, and a Markdown version of each
page at `page.html.md`. HTML metadata links to the page's Markdown alternative
and the documentation index.

Start at `/llms.txt`, follow the relevant tutorial or API entry, and read
[sources and verification](sources.md) before relying on a signature or default.
The full-text export is available for tools that need the entire manual; most
questions need only a few pages.

## Convention, not a correctness guarantee

The [llms.txt proposal](https://llmstxt.org/) describes a small Markdown index and
linked Markdown pages. It is an emerging documentation convention, not a
universally enforced industry standard or a guarantee that every agent will
discover the site. [Read the Docs supports these exports](https://docs.readthedocs.com/platform/stable/reference/llms-txt.html).
Guidance checked on 2026-09-13.

We use the existing `sphinx_llm.txt` extension to generate exports. No model calls
or generated summaries are enabled. API source links use Sphinx's `viewcode`
extension, supplied with the recorded source text rather than imported telescope
packages. The separate baseline GitHub links identify the source commit; the
local source views show the exact bytes used for this documentation snapshot.

## Authority and scope

- Tutorials explain software use and distinguish checked code from historical
  results. They are not permission to operate the telescope.
- The [team wiki](knowledge.md) holds dated array state, operational decisions,
  recipe corrections and retractions. Consult it before interpreting an old plot
  as evidence about today's instrument.
- Repository `CLAUDE.md` and `AGENTS.md` files govern changes to those repositories.
  This site's `llms.txt` is a reading index, not a replacement for those rules.
- Deployment and hardware changes require the relevant human approval. A command
  labelled dry-run must be checked for filesystem and registry side effects too.
