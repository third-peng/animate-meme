# Platform Presets

Presets are conservative defaults. Check the target app if the user has strict delivery requirements.

| Preset | Max Edge | FPS | Notes |
| --- | ---: | ---: | --- |
| `chat` | 512 | 16 | Default for general chat apps. |
| `small` | 320 | 12 | Use when file size matters most. |
| `sticker` | 512 | 16 | Preserve transparency when possible. |
| `web` | 720 | 20 | Larger preview for browser or social posts. |

## Format Guidance

- GIF: broad compatibility, larger files, limited colors.
- WebP: smaller and cleaner, but not universal in every app.
- MP4: smooth and compact, but no transparency and not always treated as a sticker.

## Size Reduction Order

1. Lower `--max-size`.
2. Lower `--fps`.
3. Lower `--duration`.
4. Use WebP instead of GIF.
5. Run `optimize_output.py --colors 96` for GIFs.
