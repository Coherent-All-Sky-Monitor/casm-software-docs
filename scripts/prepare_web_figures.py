"""Encode the solar plot for web delivery without rerunning its analysis.

The original PNG remains available for full-resolution inspection.
"""

from pathlib import Path

from PIL import Image


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / "docs/_static/tutorials/solar/solar-waterfall.png"
    destination = source.with_suffix(".webp")
    with Image.open(source) as figure:
        figure.convert("RGB").save(destination, "WEBP", quality=90, method=6)
    print(f"Solar plot: {source.stat().st_size:,} → {destination.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
