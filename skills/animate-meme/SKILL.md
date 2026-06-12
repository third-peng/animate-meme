---
name: animate-meme
description: Turn static meme images into short looping animated memes. Use when Codex needs to animate PNG, JPG, JPEG, or WebP reaction images into GIF, animated WebP, or optional MP4 outputs with deterministic effects, automatic style recommendation, subject detection, cutout-style motion, captioning, batch variants, platform presets, resizing, size optimization, or optional AI-enhanced expression/motion workflows.
---

# Animate Meme

Use this skill to convert a static meme image into a short looping animation suitable for chat apps, social posts, or web previews.

## Quick Workflow

1. Inspect the source image with `scripts/inspect_media.py` when dimensions, format, transparency, subject coverage, or size constraints matter.
2. Use `--style auto` unless the user asks for a specific effect.
3. Use `--subject-mode auto` by default. Use `--subject-mode full` for posters/screenshots where the whole image should move.
4. Generate one output or several candidates with `scripts/animate_meme.py`.
5. If the output is too large, run `scripts/optimize_output.py` or regenerate with a smaller preset.
6. Use `references/ai-enhancement.md` only when the user explicitly asks for organic expression changes, blinking, mouth motion, new motion content, or image-to-video.
7. Return the generated file path and mention any dependency limitation if MP4/video encoding was requested.

## Default Choices

- Prefer GIF for maximum compatibility.
- Prefer animated WebP when quality and small file size matter.
- Use MP4 only when the user asks for video output or a platform needs it.
- Default to `--preset chat`, `--style auto`, `--subject-mode auto`, `--duration 1.2`, `--fps 16`, and a looping animation.
- Keep animations short, readable, and seamless.
- Generate 3 to 5 variants when the user says "give me options", "try several", or does not know which effect fits.

## Core Commands

Create a shaking GIF:

```bash
python scripts/animate_meme.py input.png --style shake --output output.gif
```

Create an automatically chosen GIF:

```bash
python scripts/animate_meme.py input.png --style auto --subject-mode auto --output output.gif
```

Create an angry impact loop with caption text:

```bash
python scripts/animate_meme.py input.jpg --style impact --text "NOPE" --preset chat --output nope.gif
```

Create three candidate animations:

```bash
python scripts/animate_meme.py input.png --style auto --variants 3 --preset chat
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

- Use `auto` first when the user provides an image and no exact animation style.
- Use `shake` for surprised, angry, chaotic, or denial memes.
- Use `impact` for punchline, rage, rejection, or exaggerated reaction memes.
- Use `bounce` for cute, happy, smug, or light reactions.
- Use `rotate` for confused, dizzy, skeptical, or playful reactions.
- Use `zoom` or `pulse` when the image needs emphasis without much motion.
- Use `drift` for subtle idle movement or sticker-like output.
- Use `blink-text` when the main change is flashing text.

Read `references/platform-presets.md` before targeting a specific app size limit.
Read `references/ai-enhancement.md` before using generative image or video tools.

## Intelligent Mode

The script can estimate a subject bounding box from transparency or corner-background contrast. Use this for sticker-like memes, transparent PNGs, white-background reaction images, and simple character/object cutouts.

- `--subject-mode auto`: animate the detected subject when useful; otherwise animate the full image.
- `--subject-mode cutout`: force subject-style motion.
- `--subject-mode full`: animate the whole canvas.
- `--report`: write a JSON report with dimensions, subject box, coverage, chosen style, and outputs.

## Dependency Notes

The core scripts require Python 3.9+ and Pillow. MP4 output also requires `imageio` and a working video backend such as ffmpeg. If dependencies are missing, report the exact missing package and suggest installing it.

Do not use AI video generation by default. Use deterministic animation first; only use generative image/video tools when the user explicitly asks for facial expression changes, new motion content, image-to-video, or a highly organic result that cannot be achieved with transforms.
