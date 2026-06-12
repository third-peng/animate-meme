---
name: animate-meme
description: Turn static meme images into short looping animated memes. Use when Codex needs to animate PNG, JPG, JPEG, or WebP reaction images into GIF, animated WebP, or optional MP4 outputs with effects such as shake, bounce, zoom, rotate, pulse, impact, drift, blinking text, captions, platform presets, resizing, and size optimization.
---

# Animate Meme

Use this skill to convert a static meme image into a short looping animation suitable for chat apps, social posts, or web previews.

## Quick Workflow

1. Inspect the source image with `scripts/inspect_media.py` when dimensions, format, transparency, or size constraints matter.
2. Choose a recipe from `references/animation-recipes.md` based on the image mood and user request.
3. Generate the animation with `scripts/animate_meme.py`.
4. If the output is too large, run `scripts/optimize_output.py` or regenerate with a smaller preset.
5. Return the generated file path and mention any dependency limitation if MP4/video encoding was requested.

## Default Choices

- Prefer GIF for maximum compatibility.
- Prefer animated WebP when quality and small file size matter.
- Use MP4 only when the user asks for video output or a platform needs it.
- Default to `--preset chat`, `--duration 1.2`, `--fps 16`, and a looping animation.
- Keep animations short, readable, and seamless.

## Core Commands

Create a shaking GIF:

```bash
python scripts/animate_meme.py input.png --style shake --output output.gif
```

Create an angry impact loop with caption text:

```bash
python scripts/animate_meme.py input.jpg --style impact --text "NOPE" --preset chat --output nope.gif
```

Create animated WebP:

```bash
python scripts/animate_meme.py input.png --style bounce --format webp --output output.webp
```

Inspect an image:

```bash
python scripts/inspect_media.py input.png
```

Optimize a generated GIF/WebP:

```bash
python scripts/optimize_output.py output.gif --max-size 512 --colors 96
```

## Style Selection

- Use `shake` for surprised, angry, chaotic, or denial memes.
- Use `impact` for punchline, rage, rejection, or exaggerated reaction memes.
- Use `bounce` for cute, happy, smug, or light reactions.
- Use `rotate` for confused, dizzy, skeptical, or playful reactions.
- Use `zoom` or `pulse` when the image needs emphasis without much motion.
- Use `drift` for subtle idle movement or sticker-like output.
- Use `blink-text` when the main change is flashing text.

Read `references/platform-presets.md` before targeting a specific app size limit.

## Dependency Notes

The core scripts require Python 3.9+ and Pillow. MP4 output also requires `imageio` and a working video backend such as ffmpeg. If dependencies are missing, report the exact missing package and suggest installing it.

Do not use AI video generation by default. Use deterministic animation first; only use generative image/video tools when the user explicitly asks for facial expression changes, new motion content, or a highly organic result that cannot be achieved with transforms.
