project = "CASM Software"
author = "CASM collaboration"
copyright = "2026, CASM collaboration"
extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
exclude_patterns = ["_build", "_downloads", "Thumbs.db", ".DS_Store"]
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
    "dark_css_variables": {"color-brand-primary": "#79c8bc", "color-brand-content": "#79c8bc"},
    "sidebar_hide_name": False,
}
html_show_sphinx = False
html_show_copyright = True
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 4
