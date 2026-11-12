"""Resize article images from a JSON manifest on stdin, without changing originals."""

import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_SIZE = 1600


def resize(source, destination):
    with Image.open(source) as original:
        if getattr(original, "is_animated", False):
            raise ValueError(f"Animated article images are not supported: {source}")
        image = ImageOps.exif_transpose(original)
        image.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        suffix = destination.suffix.lower()
        if suffix in (".jpg", ".jpeg"):
            image.convert("RGB").save(destination, quality=85, optimize=True)
        elif suffix == ".png":
            image.save(destination, optimize=True)
        elif suffix == ".webp":
            image.save(destination, quality=85, method=6)
        else:
            raise ValueError(f"Unsupported article image format: {source}")


if __name__ == "__main__":
    for entry in json.load(sys.stdin):
        resize(entry["source"], entry["destination"])
