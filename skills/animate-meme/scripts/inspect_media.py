#!/usr/bin/env python3
"""Inspect a meme image or animation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def require_pillow():
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Missing dependency: Pillow. Install with `pip install pillow`.") from exc
    return Image


def average_corner_color(img, sample: int = 10) -> tuple[int, int, int, int]:
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    sample = max(1, min(sample, rgba.width, rgba.height))
    coords = []
    for y in range(sample):
        for x in range(sample):
            coords.extend(
                [
                    (x, y),
                    (rgba.width - 1 - x, y),
                    (x, rgba.height - 1 - y),
                    (rgba.width - 1 - x, rgba.height - 1 - y),
                ]
            )
    totals = [0, 0, 0, 0]
    for x, y in coords:
        pixel = pixels[x, y]
        for index in range(4):
            totals[index] += pixel[index]
    count = max(1, len(coords))
    return tuple(round(value / count) for value in totals)  # type: ignore[return-value]


def detect_subject_bbox(img, tolerance: int = 34) -> tuple[int, int, int, int]:
    rgba = img.convert("RGBA")
    alpha_bbox = rgba.getchannel("A").point(lambda value: 255 if value > 20 else 0).getbbox()
    whole = (0, 0, rgba.width, rgba.height)
    if alpha_bbox and alpha_bbox != whole:
        return alpha_bbox

    bg = average_corner_color(rgba)
    pixels = rgba.load()
    min_x, min_y = rgba.width, rgba.height
    max_x, max_y = -1, -1
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a <= 20:
                continue
            diff = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if diff > tolerance:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x < min_x or max_y < min_y:
        return whole
    return (min_x, min_y, max_x + 1, max_y + 1)


def inspect(path: Path) -> dict:
    Image = require_pillow()
    with Image.open(path) as img:
        bbox = detect_subject_bbox(img)
        coverage = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / max(1, img.width * img.height)
        info = {
            "path": str(path),
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "frames": getattr(img, "n_frames", 1),
            "animated": bool(getattr(img, "is_animated", False)),
            "has_alpha": img.mode in ("RGBA", "LA") or "transparency" in img.info,
            "background_rgba": average_corner_color(img),
            "subject_bbox": bbox,
            "subject_coverage": round(coverage, 4),
            "bytes": path.stat().st_size,
        }
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect image dimensions, format, alpha, and frame count.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a readable summary.")
    args = parser.parse_args()

    data = inspect(args.input)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for key, value in data.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
