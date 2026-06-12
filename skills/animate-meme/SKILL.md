---
name: animate-meme
description: 将静态表情包图片转换成短循环动态表情包。适用于 Codex 需要把 PNG、JPG、JPEG 或 WebP 表情图制作成 GIF、动态 WebP 或可选 MP4 的场景，支持确定性动效、自动动效推荐、主体检测、抠主体式运动、字幕、批量候选、平台预设、尺寸调整、体积优化，以及可选的 AI 表情和动作增强工作流。
---

# Animate Meme

使用这个 skill 将静态表情包图片转换成适合聊天软件、社交平台或网页预览的短循环动态表情包。

## 快速流程

1. 当尺寸、格式、透明通道、主体占比或文件大小限制很重要时，先用 `scripts/inspect_media.py` 检查源图。
2. 除非用户指定了具体效果，否则优先使用 `--style auto`。
3. 默认使用 `--subject-mode auto`。如果是海报、截图或整张图都需要一起动，使用 `--subject-mode full`。
4. 使用 `scripts/animate_meme.py` 生成一个成品，或生成多个候选版本。
5. 如果输出文件太大，运行 `scripts/optimize_output.py`，或者用更小的预设重新生成。
6. 只有当用户明确要求自然表情变化、眨眼、张嘴、新动作内容或图生视频时，才阅读并使用 `references/ai-enhancement.md`。
7. 返回生成文件路径；如果用户请求 MP4 或视频编码但依赖缺失，要说明具体限制。

## 默认选择

- 优先使用 GIF，以获得最广泛的兼容性。
- 当用户更在意质量和体积时，优先使用动态 WebP。
- 只有用户明确要求视频输出，或目标平台需要视频时，才使用 MP4。
- 默认使用 `--preset chat`、`--style auto`、`--subject-mode auto`、`--duration 1.2`、`--fps 16` 和循环动画。
- 动画要短、清晰、可读，并且循环自然。
- 当用户说“给我几个选项”“多试几个”或不确定哪种效果合适时，生成 3 到 5 个候选版本。

## 核心命令

创建抖动 GIF：

```bash
python scripts/animate_meme.py input.png --style shake --output output.gif
```

自动选择动效并生成 GIF：

```bash
python scripts/animate_meme.py input.png --style auto --subject-mode auto --output output.gif
```

创建带字幕的冲击感循环：

```bash
python scripts/animate_meme.py input.jpg --style impact --text "NOPE" --preset chat --output nope.gif
```

生成三个候选动图：

```bash
python scripts/animate_meme.py input.png --style auto --variants 3 --preset chat
```

创建动态 WebP：

```bash
python scripts/animate_meme.py input.png --style bounce --format webp --output output.webp
```

检查图片：

```bash
python scripts/inspect_media.py input.png
```

优化已生成的 GIF/WebP：

```bash
python scripts/optimize_output.py output.gif --max-size 512 --colors 96
```

## 动效选择

- 当用户只给了图片、没有指定动效时，先用 `auto`。
- `shake` 适合震惊、生气、混乱、拒绝类表情。
- `impact` 适合包袱点、暴怒、强烈拒绝、夸张反应。
- `bounce` 适合可爱、开心、得意、轻松的反应。
- `rotate` 适合疑惑、晕乎、怀疑、玩梗反应。
- `zoom` 或 `pulse` 适合强调主体，但不需要太多运动的图。
- `drift` 适合轻微待机感或贴纸式输出。
- `blink-text` 适合主要变化是文字闪烁的图。

针对具体平台体积限制时，先阅读 `references/platform-presets.md`。
使用生成式图片或视频工具前，先阅读 `references/ai-enhancement.md`。

## 智能模式

脚本可以根据透明通道或角落背景色差估算主体边界框。这个能力适合贴纸类表情、透明 PNG、白底反应图，以及简单角色或物体抠图。

- `--subject-mode auto`：在合适时让检测到的主体单独运动，否则移动整张图。
- `--subject-mode cutout`：强制使用主体式运动。
- `--subject-mode full`：移动整张画布。
- `--report`：写出 JSON 报告，包含尺寸、主体框、主体占比、选择的动效和输出文件。

## 依赖说明

核心脚本需要 Python 3.9+ 和 Pillow。MP4 输出还需要 `imageio` 以及可用的视频后端，例如 ffmpeg。依赖缺失时，要报告具体缺少的包，并建议安装方式。

默认不要使用 AI 视频生成。优先使用确定性动画；只有当用户明确要求表情变化、新动作内容、图生视频，或需要普通几何变换无法实现的自然效果时，才使用生成式图片或视频工具。
