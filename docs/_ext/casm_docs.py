"""Serve recorded Python source to Sphinx without importing telescope packages."""
from pathlib import Path
import posixpath
from urllib.parse import urlsplit

from docutils import nodes
from sphinx import addnodes
from sphinx.pycode import ModuleAnalyzer


def find_source(app, module):
    root = Path(app.srcdir) / "_code"
    path = root.joinpath(*module.split(".")).with_suffix(".py")
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        # An empty result prevents viewcode from falling back to package imports.
        return "", {}
    source = path.read_text()
    analyzer = ModuleAnalyzer.for_string(source, module)
    analyzer.find_tags()
    return source, analyzer.tags


def page_context(app, pagename, templatename, context, doctree):
    if doctree is not None and app.builder.name == "html":
        context["metatags"] += (
            f'<link rel="alternate" type="text/markdown" '
            f'href="{context["pathto"](pagename + ".html.md", 1)}">\n'
            f'<link rel="describedby" href="{context["pathto"]("llms.txt", 1)}">\n'
        )


def markdown_figures(app, doctree, docname):
    """Preserve scientific captions and page-relative images in Markdown exports.

    sphinx-markdown-builder 0.6.11 drops caption nodes and emits image paths
    relative to the documentation root, even for nested pages.
    """
    if app.builder.name != "llms-markdown":
        return
    for caption in list(doctree.findall(nodes.caption)):
        caption.replace_self(nodes.paragraph("", "", *caption.children))
    for download in doctree.findall(addnodes.download_reference):
        if download.get("filename"):
            download["refuri"] = posixpath.relpath(
                "_downloads/" + download["filename"], posixpath.dirname(docname) or "."
            )
    for picture in list(doctree.findall(nodes.image)):
        uri = picture["uri"]
        if not urlsplit(uri).scheme and not uri.startswith("/"):
            picture["uri"] = posixpath.relpath(uri, posixpath.dirname(docname) or ".")
        if isinstance(picture.parent, nodes.figure):
            picture.replace_self(nodes.paragraph("", "", picture.deepcopy()))


def setup(app):
    app.connect("viewcode-find-source", find_source)
    app.connect("html-page-context", page_context)
    app.connect("doctree-resolved", markdown_figures)
    return {"version": "1", "parallel_read_safe": True, "parallel_write_safe": True}
