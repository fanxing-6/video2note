# video2note

把 Bilibili、YouTube、TikTok 或 Douyin 上的讲座、直播回放、教程、技术分享视频，整理成结构化的中文 LaTeX 笔记，并最终渲染为 PDF。

这个 skill 面向长视频笔记生产，默认工作流包括：

- 使用 `faster-whisper` + `whisper-large-v3` 做语音转文字
- 使用 `PaddleOCR` + `PP-OCRv5` 做画面 OCR
- 从视频中抽取关键帧作为插图
- 输出可编译的 LaTeX 文稿和最终 PDF

## 仓库结构

```text
skills/
  video2note/
    SKILL.md
    agents/openai.yaml
    assets/notes-template.tex
    runtime/
```

## 安装

如果你已经安装了 Codex 自带的 skill 安装器，可以直接从 GitHub 安装：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo fanxing-6/video2note \
  --path skills/video2note
```

安装完成后，重启 Codex 以加载这个 skill。

## 运行时环境

运行时脚本位于：

```bash
skills/video2note/runtime/
```

安装后的典型使用方式：

```bash
cd ~/.codex/skills/video2note/runtime
./setup_runtime.sh
source ./env.sh
```

## 说明

- 本仓库刻意排除了本地缓存、虚拟环境、转写结果、下载视频和模型权重，不会把这些内容提交到 GitHub。
- 默认本地工作流不依赖任何 API Key。
- 对于 Bilibili，高分辨率视频流可能需要浏览器 cookies 才能下载。
- 对于 TikTok / Douyin，默认通过 `dlpanda` 解析 HTML 并提取直连媒体 URL，不依赖登录 cookies。
