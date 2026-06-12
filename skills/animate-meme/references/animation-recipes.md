# 动效配方

把这些配方作为起点。根据源图内容调整时长、帧率和字幕。

## 反应类循环

| 情绪/用途 | 动效 | 推荐参数 |
| --- | --- | --- |
| 生气 / 强调 | `impact` | `--duration 1 --fps 18 --text "NO"` |
| 震惊 / 混乱 | `shake` | `--duration 0.9 --fps 18` |
| 可爱 / 开心 | `bounce` | `--duration 1.2 --fps 16` |
| 疑惑 / 晕乎 | `rotate` | `--duration 1.4 --fps 16` |
| 得意 / 调侃 | `pulse` | `--duration 1.2 --fps 14` |
| 待机贴纸 | `drift` | `--duration 1.8 --fps 14` |
| 字幕强调 | `blink-text` | `--text "..." --duration 1.2 --fps 12` |
| 不确定 / 自动选择 | `auto` | `--variants 3 --subject-mode auto` |

## 循环规则

- 第一帧和最后一帧要尽量接近，避免循环时跳变。
- 使用正弦或余弦运动，让循环更顺滑。
- 强烈抖动的循环最好控制在 1 秒以内。
- 字幕要大、对比度高，并带描边。
- GIF 不要堆太多帧，通常 12 到 18 FPS 已经足够。

## 常用命令

```bash
python scripts/animate_meme.py input.png --style auto --subject-mode auto --output auto.gif
python scripts/animate_meme.py input.png --style auto --variants 4 --preset chat
python scripts/animate_meme.py input.png --style impact --preset chat --output impact.gif
python scripts/animate_meme.py input.png --style bounce --format webp --output bounce.webp
python scripts/animate_meme.py input.png --style blink-text --text "HELP" --output help.gif
```

## 主体模式

- 透明 PNG、贴纸图、白底表情图优先用 `--subject-mode auto`。
- 当角色或物体应该相对背景独立运动时，用 `--subject-mode cutout`。
- 当图片是截图、海报，或重要文字分布在整张图上时，用 `--subject-mode full`。

## 批量候选配方

当用户没有明确指定情绪或动效时，生成多个候选 GIF：

```bash
python scripts/animate_meme.py input.png --style auto --variants 5 --preset chat
```

第一个输出会使用推荐动效。后续输出会尝试 impact、bounce、shake、pulse、drift 等高价值备选效果。
