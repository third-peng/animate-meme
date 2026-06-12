# Animation Recipes

Use these recipes as starting points. Tune duration, FPS, and caption text to match the source image.

## Reaction Loops

| Mood | Style | Suggested Options |
| --- | --- | --- |
| Angry / emphatic | `impact` | `--duration 1 --fps 18 --text "NO"` |
| Shocked / chaotic | `shake` | `--duration 0.9 --fps 18` |
| Cute / happy | `bounce` | `--duration 1.2 --fps 16` |
| Confused / dizzy | `rotate` | `--duration 1.4 --fps 16` |
| Smug / teasing | `pulse` | `--duration 1.2 --fps 14` |
| Idle sticker | `drift` | `--duration 1.8 --fps 14` |
| Caption emphasis | `blink-text` | `--text "..." --duration 1.2 --fps 12` |

## Looping Rules

- Make the first and last frame visually close so the loop does not pop.
- Use sine/cosine motion for smooth repeatable loops.
- Keep shake loops under 1 second when they are intense.
- Keep text large, high contrast, and outlined.
- Avoid too many frames for GIFs; 12 to 18 FPS is usually enough.

## Common Commands

```bash
python scripts/animate_meme.py input.png --style impact --preset chat --output impact.gif
python scripts/animate_meme.py input.png --style bounce --format webp --output bounce.webp
python scripts/animate_meme.py input.png --style blink-text --text "HELP" --output help.gif
```
