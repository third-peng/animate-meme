# AI Enhancement Workflow

Use this reference only when deterministic transforms are not enough and the user explicitly wants organic motion, expression changes, or image-to-video.

## When To Use AI

- Blinking eyes, eye darts, mouth opening/closing, or breathing that cannot be made with simple transforms.
- Changing emotion, such as neutral to angry, happy, smug, crying, or shocked.
- Creating new in-between art for a character, not just moving the source image.
- Image-to-video output where the user accepts less deterministic results.

## Preferred Order

1. Create a deterministic GIF/WebP first with `scripts/animate_meme.py`.
2. If the user wants more life, generate or edit a small number of expression keyframes.
3. Assemble those keyframes with deterministic timing, captions, and optimization.
4. Keep the final loop short and inspect the output before returning it.

## Keyframe Strategy

Use 3 to 6 keyframes for expression animation:

| Motion | Keyframes |
| --- | --- |
| Blink | open, half-closed, closed, half-closed, open |
| Mouth | closed, small open, wide open, small open, closed |
| Angry pulse | normal, intense face, zoomed intense, normal |
| Cute bounce | normal, eyes-smile, normal |

After generating keyframes, pass them through a deterministic assembly step. Do not rely on a long AI video when a short keyframe loop will be cleaner.

## Prompt Shape For Image Editing

Use concise instructions that preserve identity and composition:

```text
Create a transparent-background variant of this meme character with the same art style and pose, but with eyes closed for a blink frame. Preserve the outline, colors, proportions, and canvas alignment.
```

```text
Create a second keyframe of this meme character with a slightly open mouth, same style, same lighting, same canvas alignment, no new background.
```

## Image-To-Video Guardrails

- Use image-to-video only when the user asks for video-like motion.
- Request a seamless loop, minimal camera movement, and no new text.
- Keep duration around 1 to 2 seconds.
- If the output changes the character identity, fall back to keyframes or deterministic transforms.

## Deliverables

When using AI enhancement, return both:

- The final GIF/WebP/MP4.
- The deterministic fallback output, unless the user only wants one file.
