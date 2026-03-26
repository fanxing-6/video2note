# video-note-renderer

Turn a Bilibili or YouTube lecture, livestream replay, tutorial, or technical talk into a structured Chinese LaTeX note and rendered PDF.

The skill is designed for long-form video note production with:

- ASR via `faster-whisper` using `whisper-large-v3`
- OCR via `PaddleOCR` using `PP-OCRv5`
- figure extraction from key video frames
- a compileable LaTeX output and final PDF

## Repository Layout

```text
skills/
  video-note-renderer/
    SKILL.md
    agents/openai.yaml
    assets/notes-template.tex
    runtime/
```

## Install

If you already have the Codex skill installer, install this skill from GitHub with:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo fanxing-6/video-note-renderer \
  --path skills/video-note-renderer
```

After installation, restart Codex to load the new skill.

## Runtime Setup

The runtime helpers live under:

```bash
skills/video-note-renderer/runtime/
```

From an installed skill directory:

```bash
cd ~/.codex/skills/video-note-renderer/runtime
./setup_runtime.sh
source ./env.sh
```

## Notes

- This repository intentionally excludes local caches, virtual environments, transcripts, downloaded videos, and model weights.
- No API keys are required for the default local workflow.
- For Bilibili, high-resolution formats may require browser cookies.
