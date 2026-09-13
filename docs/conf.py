import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_ext"))

project = "CASM Software"
author = "CASM collaboration"
copyright = "2026, CASM collaboration"
extensions = ["myst_parser", "sphinx.ext.viewcode", "sphinx_llm.txt", "casm_docs"]
source_suffix = {".md": "markdown"}
exclude_patterns = ["_build", "_downloads", "_code", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
html_title = "CASM Software"
html_static_path = ["_static"]
html_css_files = ["casm.css"]
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#176b64", "color-brand-content": "#176b64",
        "color-background-primary": "#fcfcf9", "color-background-secondary": "#f1f3ef",
        "font-stack": "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
    },
    "dark_css_variables": {
        "color-brand-primary": "#afc4e2", "color-brand-content": "#afc4e2",
        "color-background-primary": "#131416",
        "color-background-secondary": "#0c0d0f",
        "color-sidebar-background": "#0c0d0f",
        "color-sidebar-link-text": "#c7ccd4",
        "color-sidebar-link-text--top-level": "#d7dbe2",
        "color-sidebar-caption-text": "#989faa",
        "color-sidebar-item-background--current": "#20242b",
        "color-sidebar-search-background": "#14161a",
    },
    "sidebar_hide_name": False,
}
html_show_sphinx = False
html_show_copyright = True
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 4
viewcode_follow_imported_members = False
llms_txt_description = (
    "CASM scientific software: tutorials, data contracts and API references. "
    "Read sources.html.md for pinned software revisions and verification limits. "
    "Operational commands require human approval; these docs do not describe live array state."
)
llms_txt_build_parallel = False
llms_txt_summary_enabled = False
# Upstream manuals are downloads, not reviewed tutorial text.
llms_txt_exclude = ["_downloads/**", "_static/**", "_code/**"]
