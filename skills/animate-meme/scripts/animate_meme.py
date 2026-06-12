#!/usr/bin/env python3
"""Turn a static meme image into a short looping animation."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path


STYLES = ["shake", "bounce", "zoom", "rotate", "pulse", "impact", "drift", "blink-text"]
PRESETS = {
    "chat": {"max_size": 512, "fps": 16},
    "small": {"max_size": 320, "fps": 12},
    "sticker": {"max_size": 512, "fps": 16},
    "web": {"max_size": 720, "fps": 20},
}


@dataclass
class ImageAnalysis:
    width: int
    height: int
    has_alpha: bool
    subject_bbox: tuple[int, int, int, int]
    subject_coverage: float
    background_rgba: tuple[int, int, int, int]
    recommended_style: str


def require_pillow():
    try:
        from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageFilter
    except ImportError as exc:
        raise SystemExit("Missing dependency: Pillow. Install with `pip install pillow`.") from exc
    return Image, ImageColor, ImageDraw, ImageFont, ImageFilter


def parse_background(value: str):
    _, ImageColor, _, _, _ = require_pillow()
    if value == "transparent":
        return (0, 0, 0, 0)
    try:
        rgb = ImageColor.getrgb(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid background color: {value}") from exc
    if len(rgb) == 3:
        return (*rgb, 255)
    return rgb


def output_path_for(input_path: Path, fmt: str, style: str | None = None) -> Path:
    suffix = ".gif" if fmt == "gif" else f".{fmt}"
    label = f".{style}" if style else ".animated"
    return input_path.with_name(f"{input_path.stem}{label}{suffix}")


def fit_image(img, max_size: int):
    Image, _, _, _, _ = require_pillow()
    img = img.convert("RGBA")
    scale = min(1.0, max_size / max(img.width, img.height))
    if scale >= 1:
        return img
    size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    return img.resize(size, resample=Image.Resampling.LANCZOS)


def clamp_bbox(bbox: tuple[int, int, int, int], width: int, height: int, pad: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = bbox
    return (
        max(0, left - pad),
        max(0, top - pad),
        min(width, right + pad),
        min(height, bottom + pad),
    )


def average_corner_color(img, sample: int = 10) -> tuple[int, int, int, int]:
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    coords = []
    sample = max(1, min(sample, rgba.width, rgba.height))
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
    alpha = rgba.getchannel("A")
    alpha_bbox = alpha.point(lambda value: 255 if value > 20 else 0).getbbox()
    whole = (0, 0, rgba.width, rgba.height)
    if alpha_bbox and alpha_bbox != whole:
        return clamp_bbox(alpha_bbox, rgba.width, rgba.height, max(2, round(min(rgba.size) * 0.02)))

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
    return clamp_bbox((min_x, min_y, max_x + 1, max_y + 1), rgba.width, rgba.height, max(3, round(min(rgba.size) * 0.03)))


def recommend_style(path: Path, img, text: str | None, bbox: tuple[int, int, int, int], coverage: float) -> str:
    name = path.stem.lower()
    if text:
        return "impact"
    if any(token in name for token in ["angry", "rage", "nope", "no", "rush", "go", "run", "chong"]):
        return "impact"
    if any(token in name for token in ["cute", "cat", "love", "happy", "smile"]):
        return "bounce"
    if any(token in name for token in ["confused", "what", "why", "dizzy"]):
        return "rotate"
    if img.width > img.height * 1.35:
        return "impact"
    if coverage < 0.65:
        return "bounce"
    return "shake"


def analyze_image(path: Path, img, text: str | None) -> ImageAnalysis:
    bbox = detect_subject_bbox(img)
    box_area = max(1, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
    coverage = box_area / max(1, img.width * img.height)
    has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
    style = recommend_style(path, img, text, bbox, coverage)
    return ImageAnalysis(
        width=img.width,
        height=img.height,
        has_alpha=has_alpha,
        subject_bbox=bbox,
        subject_coverage=coverage,
        background_rgba=average_corner_color(img),
        recommended_style=style,
    )


def motion(style: str, phase: float, width: int, height: int) -> dict:
    wave = math.sin(math.tau * phase)
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
        values.update(dx=hit * unit * 1.8, scale=1.0 + hit * 0.24 + rebound * 0.035, angle=rebound * 3.5)
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
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
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


def draw_caption(frame, text: str, font_path: str | None, position: str):
    _, _, ImageDraw, ImageFont, _ = require_pillow()
    draw = ImageDraw.Draw(frame)
    font_size = max(18, round(frame.height * 0.13))
    font = load_font(ImageFont, font_path, font_size)
    margin = max(8, round(frame.width * 0.035))
    stroke = max(2, font_size // 12)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = max(margin, (frame.width - text_w) // 2)
    if position == "top":
        y = margin
    elif position == "center":
        y = max(margin, (frame.height - text_h) // 2)
    else:
        y = frame.height - text_h - margin * 2
    draw.text((x, y), text, font=font, fill="white", stroke_width=stroke, stroke_fill="black")


def build_subject_mask(crop, bg_rgba: tuple[int, int, int, int], tolerance: int = 34):
    Image, _, _, _, ImageFilter = require_pillow()
    rgba = crop.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getbbox() and alpha.getbbox() != (0, 0, rgba.width, rgba.height):
        return alpha

    mask = Image.new("L", rgba.size, 0)
    src = rgba.load()
    dst = mask.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = src[x, y]
            if a <= 20:
                continue
            diff = abs(r - bg_rgba[0]) + abs(g - bg_rgba[1]) + abs(b - bg_rgba[2])
            if diff > tolerance:
                dst[x, y] = 255
    return mask.filter(ImageFilter.GaussianBlur(radius=0.8)).point(lambda value: 255 if value > 16 else 0)


def prepare_layers(base, subject_mode: str, analysis: ImageAnalysis):
    Image, _, _, _, ImageFilter = require_pillow()
    if subject_mode == "full":
        return None, base
    if subject_mode == "auto" and analysis.subject_coverage > 0.86 and not analysis.has_alpha:
        return None, base

    bbox = analysis.subject_bbox
    subject = base.crop(bbox).convert("RGBA")
    subject.putalpha(build_subject_mask(subject, analysis.background_rgba))
    if analysis.has_alpha:
        background = Image.new("RGBA", base.size, (0, 0, 0, 0))
    else:
        background = base.copy()
        fill = Image.new("RGBA", base.size, analysis.background_rgba)
        soft = background.filter(ImageFilter.GaussianBlur(radius=3))
        background = Image.blend(fill, soft, 0.18)
    return background, subject


def paste_transformed(canvas, layer, center: tuple[float, float], transform: dict):
    Image, _, _, _, _ = require_pillow()
    scale = transform["scale"]
    resized = layer.resize(
        (max(1, round(layer.width * scale)), max(1, round(layer.height * scale))),
        resample=Image.Resampling.LANCZOS,
    )
    rotated = resized.rotate(transform["angle"], resample=Image.Resampling.BICUBIC, expand=True)
    x = round(center[0] - rotated.width / 2 + transform["dx"])
    y = round(center[1] - rotated.height / 2 + transform["dy"])
    canvas.alpha_composite(rotated, (x, y))


def composite(base, canvas_size: tuple[int, int], transform: dict, background_color, layers, analysis: ImageAnalysis):
    Image, _, _, _, _ = require_pillow()
    canvas = Image.new("RGBA", canvas_size, background_color)
    pad_x = (canvas.width - base.width) / 2
    pad_y = (canvas.height - base.height) / 2
    background, subject = layers
    if background is None:
        paste_transformed(canvas, base, (canvas.width / 2, canvas.height / 2), transform)
        return canvas

    canvas.alpha_composite(background, (round(pad_x), round(pad_y)))
    left, top, right, bottom = analysis.subject_bbox
    subject_center = (pad_x + (left + right) / 2, pad_y + (top + bottom) / 2)
    paste_transformed(canvas, subject, subject_center, transform)
    return canvas


def save_gif(frames, output: Path, duration_ms: int, colors: int):
    Image, _, _, _, _ = require_pillow()
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


def resolve_format(args) -> str:
    fmt = args.format or (args.output.suffix.lower().lstrip(".") if args.output else "gif")
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in {"gif", "webp", "mp4"}:
        raise SystemExit("Supported output formats: gif, webp, mp4.")
    return fmt


def write_frames(frames, output: Path, fmt: str, duration_ms: int, fps: int, colors: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "gif":
        save_gif(frames, output, duration_ms, colors)
    elif fmt == "webp":
        save_webp(frames, output, duration_ms)
    else:
        save_mp4(frames, output, fps)


def build_frames(args, base, analysis: ImageAnalysis, style: str):
    preset = PRESETS[args.preset]
    fps = args.fps or preset["fps"]
    frame_count = max(2, round(args.duration * fps))
    background_color = parse_background(args.background)
    pad = max(16, round(max(base.width, base.height) * 0.16))
    canvas_size = (base.width + pad * 2, base.height + pad * 2)
    layers = prepare_layers(base, args.subject_mode, analysis)
    frames = []

    for index in range(frame_count):
        phase = index / frame_count
        transform = motion(style, phase, base.width, base.height)
        frame = composite(base, canvas_size, transform, background_color, layers, analysis)
        if args.text and transform["text_on"]:
            draw_caption(frame, args.text, args.font, args.caption_position)
        frames.append(frame)
    return frames, max(20, round(1000 / fps)), fps


def variant_styles(primary: str, count: int) -> list[str]:
    ordered = [primary, "impact", "bounce", "shake", "pulse", "drift", "rotate", "blink-text"]
    result = []
    for style in ordered:
        if style not in result:
            result.append(style)
        if len(result) >= count:
            break
    return result


def animate(args) -> list[Path]:
    Image, _, _, _, _ = require_pillow()
    preset = PRESETS[args.preset]
    max_size = args.max_size or preset["max_size"]
    fmt = resolve_format(args)

    with Image.open(args.input) as source:
        base = fit_image(source, max_size)
    analysis = analyze_image(args.input, base, args.text)

    primary_style = analysis.recommended_style if args.style == "auto" else args.style
    styles = variant_styles(primary_style, args.variants)
    outputs = []
    for style in styles:
        output = args.output
        if args.variants > 1 or output is None:
            output = output_path_for(args.input, fmt, style)
        frames, duration_ms, fps = build_frames(args, base, analysis, style)
        write_frames(frames, output, fmt, duration_ms, fps, args.colors)
        outputs.append(output)

    if args.report:
        report = {
            "input": str(args.input),
            "outputs": [str(path) for path in outputs],
            "analysis": {
                "width": analysis.width,
                "height": analysis.height,
                "has_alpha": analysis.has_alpha,
                "subject_bbox": analysis.subject_bbox,
                "subject_coverage": round(analysis.subject_coverage, 4),
                "recommended_style": analysis.recommended_style,
            },
        }
        report_path = args.report if isinstance(args.report, Path) else args.input.with_suffix(".animate-report.json")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Animate a static meme into a short loop.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--style", choices=["auto", *STYLES], default="auto")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="chat")
    parser.add_argument("--format", choices=["gif", "webp", "mp4"])
    parser.add_argument("--duration", type=float, default=1.2)
    parser.add_argument("--fps", type=int)
    parser.add_argument("--max-size", type=int)
    parser.add_argument("--background", default="transparent", help="transparent, #RRGGBB, or a CSS color name.")
    parser.add_argument("--subject-mode", choices=["full", "auto", "cutout"], default="auto")
    parser.add_argument("--variants", type=int, default=1, help="Generate several style candidates.")
    parser.add_argument("--text", help="Optional caption text.")
    parser.add_argument("--caption-position", choices=["top", "center", "bottom"], default="bottom")
    parser.add_argument("--font", help="Optional TrueType font path.")
    parser.add_argument("--colors", type=int, default=128, help="GIF palette color count.")
    parser.add_argument("--report", nargs="?", const=True, type=Path, help="Write a JSON analysis report.")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    if args.variants < 1:
        raise SystemExit("--variants must be at least 1.")
    outputs = animate(args)
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
