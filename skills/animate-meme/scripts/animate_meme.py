#!/usr/bin/env python3
"""Turn a static meme image into a short looping animation."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


PRESETS = {
    "chat": {"max_size": 512, "fps": 16},
    "small": {"max_size": 320, "fps": 12},
    "sticker": {"max_size": 512, "fps": 16},
    "web": {"max_size": 720, "fps": 20},
}


def require_pillow():
    try:
        from PIL import Image, ImageColor, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit("Missing dependency: Pillow. Install with `pip install pillow`.") from exc
    return Image, ImageColor, ImageDraw, ImageFont


def parse_background(value: str):
    Image, ImageColor, _, _ = require_pillow()
    if value == "transparent":
        return (0, 0, 0, 0)
    try:
        rgb = ImageColor.getrgb(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid background color: {value}") from exc
    if len(rgb) == 3:
        return (*rgb, 255)
    return rgb


def output_path_for(input_path: Path, fmt: str) -> Path:
    suffix = ".gif" if fmt == "gif" else f".{fmt}"
    return input_path.with_name(f"{input_path.stem}.animated{suffix}")


def fit_image(img, max_size: int):
    Image, _, _, _ = require_pillow()
    img = img.convert("RGBA")
    scale = min(1.0, max_size / max(img.width, img.height))
    if scale >= 1:
        return img
    size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    return img.resize(size, resample=Image.Resampling.LANCZOS)


def motion(style: str, phase: float, width: int, height: int) -> dict:
    wave = math.sin(math.tau * phase)
    snap = math.sin(math.tau * phase * 2)
    unit = max(4, min(width, height) * 0.045)
    values = {"dx": 0.0, "dy": 0.0, "scale": 1.0, "angle": 0.0, "text_on": True}

    if style == "shake":
        values.update(
            dx=math.sin(math.tau * phase * 5) * unit,
            dy=math.sin(math.tau * phase * 7) * unit * 0.45,
            angle=math.sin(math.tau * phase * 6) * 2.2,
        )
    elif style == "bounce":
        values.update(dy=-abs(wave) * unit * 1.6, scale=1.0 + abs(wave) * 0.045)
    elif style == "zoom":
        values.update(scale=1.0 + (wave * 0.5 + 0.5) * 0.11)
    elif style == "rotate":
        values.update(angle=wave * 8.0, scale=1.04)
    elif style == "pulse":
        values.update(scale=1.0 + (wave * 0.5 + 0.5) * 0.15)
    elif style == "impact":
        hit = max(0.0, 1.0 - phase * 5.0)
        rebound = math.sin(math.tau * phase * 2.0) * max(0.0, 1.0 - phase)
        values.update(scale=1.0 + hit * 0.24 + rebound * 0.035, angle=rebound * 3.5)
    elif style == "drift":
        values.update(dx=wave * unit * 0.65, dy=math.cos(math.tau * phase) * unit * 0.35, scale=1.025)
    elif style == "blink-text":
        values.update(scale=1.015, text_on=phase < 0.5)
    else:
        raise SystemExit(f"Unknown style: {style}")

    return values


def load_font(ImageFont, font_path: str | None, size: int):
    candidates = []
    if font_path:
        candidates.append(font_path)
    candidates.extend(
        [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_caption(frame, text: str, font_path: str | None):
    _, _, ImageDraw, ImageFont = require_pillow()
    draw = ImageDraw.Draw(frame)
    font_size = max(18, round(frame.height * 0.13))
    font = load_font(ImageFont, font_path, font_size)
    margin = max(8, round(frame.width * 0.035))
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=max(2, font_size // 12))
    text_w = bbox[2] - bbox[0]
    x = max(margin, (frame.width - text_w) // 2)
    y = frame.height - (bbox[3] - bbox[1]) - margin * 2
    stroke = max(2, font_size // 12)
    draw.text((x, y), text, font=font, fill="white", stroke_width=stroke, stroke_fill="black")


def composite(base, canvas_size: tuple[int, int], transform: dict, background):
    Image, _, _, _ = require_pillow()
    canvas = Image.new("RGBA", canvas_size, background)
    scale = transform["scale"]
    resized = base.resize(
        (max(1, round(base.width * scale)), max(1, round(base.height * scale))),
        resample=Image.Resampling.LANCZOS,
    )
    rotated = resized.rotate(transform["angle"], resample=Image.Resampling.BICUBIC, expand=True)
    x = round((canvas.width - rotated.width) / 2 + transform["dx"])
    y = round((canvas.height - rotated.height) / 2 + transform["dy"])
    canvas.alpha_composite(rotated, (x, y))
    return canvas


def save_gif(frames, output: Path, duration_ms: int, colors: int):
    Image, _, _, _ = require_pillow()
    paletted = [
        frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=max(2, min(colors, 256)))
        for frame in frames
    ]
    paletted[0].save(
        output,
        save_all=True,
        append_images=paletted[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=True,
    )


def save_webp(frames, output: Path, duration_ms: int):
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        method=6,
        quality=84,
    )


def save_mp4(frames, output: Path, fps: int):
    try:
        import imageio.v3 as iio
        import numpy as np
    except ImportError as exc:
        raise SystemExit("MP4 output requires `pip install imageio numpy imageio-ffmpeg`.") from exc

    rgb_frames = [np.asarray(frame.convert("RGB")) for frame in frames]
    iio.imwrite(output, rgb_frames, fps=fps)


def animate(args) -> Path:
    Image, _, _, _ = require_pillow()
    preset = PRESETS[args.preset]
    fps = args.fps or preset["fps"]
    max_size = args.max_size or preset["max_size"]
    frame_count = max(2, round(args.duration * fps))
    duration_ms = max(20, round(1000 / fps))
    fmt = args.format or (args.output.suffix.lower().lstrip(".") if args.output else "gif")
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in {"gif", "webp", "mp4"}:
        raise SystemExit("Supported output formats: gif, webp, mp4.")

    with Image.open(args.input) as source:
        base = fit_image(source, max_size)

    pad = max(16, round(max(base.width, base.height) * 0.16))
    canvas_size = (base.width + pad * 2, base.height + pad * 2)
    background = parse_background(args.background)
    frames = []

    for index in range(frame_count):
        phase = index / frame_count
        transform = motion(args.style, phase, base.width, base.height)
        frame = composite(base, canvas_size, transform, background)
        if args.text and transform["text_on"]:
            draw_caption(frame, args.text, args.font)
        frames.append(frame)

    output = args.output or output_path_for(args.input, fmt)
    if fmt == "gif":
        save_gif(frames, output, duration_ms, args.colors)
    elif fmt == "webp":
        save_webp(frames, output, duration_ms)
    else:
        save_mp4(frames, output, fps)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Animate a static meme into a short loop.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--style", choices=["shake", "bounce", "zoom", "rotate", "pulse", "impact", "drift", "blink-text"], default="shake")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="chat")
    parser.add_argument("--format", choices=["gif", "webp", "mp4"])
    parser.add_argument("--duration", type=float, default=1.2)
    parser.add_argument("--fps", type=int)
    parser.add_argument("--max-size", type=int)
    parser.add_argument("--background", default="transparent", help="transparent, #RRGGBB, or a CSS color name.")
    parser.add_argument("--text", help="Optional caption text.")
    parser.add_argument("--font", help="Optional TrueType font path.")
    parser.add_argument("--colors", type=int, default=128, help="GIF palette color count.")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    output = animate(args)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
