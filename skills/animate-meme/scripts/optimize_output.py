#!/usr/bin/env python3
"""Resize and lightly optimize GIF/WebP meme animations."""

from __future__ import annotations

import argparse
from pathlib import Path


def require_pillow():
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Missing dependency: Pillow. Install with `pip install pillow`.") from exc
    return Image


def resize_frame(frame, max_size: int):
    Image = require_pillow()
    frame = frame.convert("RGBA")
    width, height = frame.size
    scale = min(1.0, max_size / max(width, height))
    if scale >= 1:
        return frame
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return frame.resize(size, resample=Image.Resampling.LANCZOS)


def optimize(input_path: Path, output_path: Path, max_size: int, colors: int) -> None:
    Image = require_pillow()
    with Image.open(input_path) as img:
        frames = []
        durations = []
        for index in range(getattr(img, "n_frames", 1)):
            img.seek(index)
            frames.append(resize_frame(img.copy(), max_size))
            durations.append(img.info.get("duration", 80))

    suffix = output_path.suffix.lower()
    if suffix == ".gif":
        paletted = [
            frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=max(2, min(colors, 256)))
            for frame in frames
        ]
        paletted[0].save(
            output_path,
            save_all=True,
            append_images=paletted[1:],
            loop=0,
            duration=durations,
            optimize=True,
            disposal=2,
        )
    elif suffix == ".webp":
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=durations,
            method=6,
            quality=82,
        )
    else:
        raise SystemExit("Only GIF and WebP optimization are supported.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Resize and optimize a GIF or animated WebP.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="Defaults to <name>.optimized<suffix>.")
    parser.add_argument("--max-size", type=int, default=512)
    parser.add_argument("--colors", type=int, default=128, help="GIF palette color count.")
    args = parser.parse_args()

    output = args.output or args.input.with_name(f"{args.input.stem}.optimized{args.input.suffix}")
    optimize(args.input, output, args.max_size, args.colors)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
