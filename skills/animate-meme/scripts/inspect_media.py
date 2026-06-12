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


def inspect(path: Path) -> dict:
    Image = require_pillow()
    with Image.open(path) as img:
        info = {
            "path": str(path),
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "frames": getattr(img, "n_frames", 1),
            "animated": bool(getattr(img, "is_animated", False)),
            "has_alpha": img.mode in ("RGBA", "LA") or "transparency" in img.info,
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
