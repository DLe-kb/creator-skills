#!/usr/bin/env python3
"""Embed local image references into a portable single-file HTML document."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path


IMAGE_SRC_PATTERN = re.compile(r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])(.*?)(\2)', re.IGNORECASE | re.DOTALL)


def embed_images(text: str, source_dir: Path) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        source = match.group(3).strip()
        if source.startswith("data:image/"):
            return match.group(0)
        if source.startswith(("http://", "https://", "//", "file://", "/", "~/")) or re.match(r"^[A-Za-z]:[\\/]", source):
            raise ValueError(f"image source must be a relative local path: {source}")

        image_path = (source_dir / source).resolve()
        if not image_path.is_file():
            raise ValueError(f"image file not found: {source}")

        mime_type = mimetypes.guess_type(image_path.name)[0]
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError(f"unsupported image type: {source}")

        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        count += 1
        return f'{match.group(1)}{match.group(2)}data:{mime_type};base64,{encoded}{match.group(4)}'

    return IMAGE_SRC_PATTERN.sub(replace, text), count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="HTML file containing relative local image paths")
    parser.add_argument("output", type=Path, help="single-file HTML output")
    args = parser.parse_args()

    source = args.input.resolve()
    output = args.output.resolve()
    text = source.read_text(encoding="utf-8")
    embedded, count = embed_images(text, source.parent)
    output.write_text(embedded, encoding="utf-8")
    print(f"EMBEDDED: {count} images -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
