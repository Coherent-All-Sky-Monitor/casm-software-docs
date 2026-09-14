"""Check generated Markdown links, scientific captions and recorded source copies."""
import ast
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_build" / "html"


def main():
    parser = MarkdownIt()
    pages = sorted(SITE.rglob("*.html.md"))
    pages = [p for p in pages if not any(part.startswith("_") for part in p.relative_to(SITE).parts)]
    assert pages, "No Markdown exports"
    checked = 0
    for path in [SITE / "llms.txt", *pages]:
        tokens = parser.parse(path.read_text())
        for block in tokens:
            for token in block.children or []:
                link = token.attrGet("href") or token.attrGet("src")
                if not link:
                    continue
                url = urlsplit(link)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (path.parent / unquote(url.path)).resolve()
                assert target.is_file(), f"{path.name}: missing {link}"
                checked += 1
    transit = (SITE / "guides/check-calibration.html.md").read_text()
    assert "../_static/tutorials/transit/cyga-beam-power.png" in transit
    assert "../_static/tutorials/transit/cyga_stationary_beam_20260805.png" in transit
    assert "_downloads/" not in (SITE / "llms.txt").read_text()

    snapshot = json.loads((ROOT / "source-snapshot.json").read_text())
    packages = {item["repository"]: item for item in snapshot["packages"]}
    for item in json.loads((ROOT / "sources.json").read_text())["packages"]:
        for relative in item["modules"]:
            copy = ROOT / "docs/_code" / relative.removeprefix("src/")
            digest = hashlib.sha256(copy.read_bytes()).hexdigest()
            assert digest == packages[item["repo"]]["files"][relative], str(copy)

    snippets = 0
    for path in (ROOT / "docs/guides").glob("*.md"):
        for token in parser.parse(path.read_text()):
            if token.type == "fence" and token.info == "python":
                ast.parse(token.content, filename=str(path))
                snippets += 1
    print(f"OK: {len(pages)} Markdown pages, {checked} links, captions, source hashes, {snippets} Python snippets")


if __name__ == "__main__":
    main()
