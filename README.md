# Animate Meme

`animate-meme` 是一个 Codex skill，用来把静态表情包图片转换成短循环动态表情包。它优先使用确定性的图片处理脚本生成 GIF、动态 WebP 或可选 MP4，也提供智能推荐、主体检测、批量候选和 AI 增强工作流说明。

## 功能

- 将 PNG、JPG、JPEG、WebP 静态图转换成动态表情包。
- 支持 `shake`、`bounce`、`zoom`、`rotate`、`pulse`、`impact`、`drift`、`blink-text` 等动效。
- 支持 `--style auto` 自动推荐动效。
- 支持 `--subject-mode auto/cutout/full`，可对贴纸、透明图或白底图进行简易主体检测。
- 支持 `--variants` 一次生成多个候选版本。
- 支持字幕、平台预设、尺寸调整和 GIF/WebP 优化。
- 提供 AI 增强参考，用于眨眼、张嘴、表情变化、图生视频等进阶场景。

## 目录结构

```text
skills/animate-meme/
  SKILL.md
  agents/openai.yaml
  scripts/
    animate_meme.py
    inspect_media.py
    optimize_output.py
  references/
    animation-recipes.md
    platform-presets.md
    ai-enhancement.md
```

## 安装

将 `skills/animate-meme` 复制到 Codex 的 skills 目录：

```powershell
Copy-Item -Path .\skills\animate-meme -Destination $env:USERPROFILE\.codex\skills\animate-meme -Recurse -Force
```

重新打开 Codex 线程后，就可以通过 `$animate-meme` 使用这个 skill。

## 依赖

核心功能需要 Python 3.9+ 和 Pillow：

```powershell
python -m pip install pillow
```

如果需要 MP4 输出，还需要：

```powershell
python -m pip install imageio numpy imageio-ffmpeg
```

## 使用示例

检查图片信息：

```powershell
python .\skills\animate-meme\scripts\inspect_media.py .\input.png
```

自动选择动效并生成 GIF：

```powershell
python .\skills\animate-meme\scripts\animate_meme.py .\input.png --style auto --subject-mode auto --output .\output.gif
```

生成冲击感表情包：

```powershell
python .\skills\animate-meme\scripts\animate_meme.py .\input.png --style impact --text "冲鸭" --output .\impact.gif
```

一次生成多个候选：

```powershell
python .\skills\animate-meme\scripts\animate_meme.py .\input.png --style auto --variants 4 --preset chat
```

生成动态 WebP：

```powershell
python .\skills\animate-meme\scripts\animate_meme.py .\input.png --style bounce --format webp --output .\bounce.webp
```

优化 GIF：

```powershell
python .\skills\animate-meme\scripts\optimize_output.py .\output.gif --max-size 512 --colors 96
```

## 在 Codex 中使用

示例提示词：

```text
使用 $animate-meme，把 D:\path\to\input.png 做成一个抖动循环 GIF，输出到 D:\path\to\output.gif。
```

```text
使用 $animate-meme，为这张表情包生成 3 个动态候选版本，优先适配聊天软件。
```

## 文档

- [Skill 使用说明](skills/animate-meme/SKILL.md)
- [动效配方](skills/animate-meme/references/animation-recipes.md)
- [平台预设](skills/animate-meme/references/platform-presets.md)
- [AI 增强工作流](skills/animate-meme/references/ai-enhancement.md)

## 说明

默认不要直接使用 AI 视频生成。先用确定性动画获得稳定、可控、体积小的结果；只有当用户明确要求自然表情变化、眨眼、张嘴、新动作内容或图生视频时，再进入 AI 增强工作流。
