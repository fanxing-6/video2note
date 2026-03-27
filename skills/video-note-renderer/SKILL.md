---
name: video-note-renderer
description: Generate a professional, figure-rich LaTeX course note and final PDF from a Bilibili or YouTube lecture, tutorial, technical talk, or livestream replay. Use when the user provides a Bilibili or YouTube URL and wants structured Chinese notes that combine the video's title, cover, key frames, charts, formulas, code, subtitle or speech-to-text explanations, and a final synthesis chapter, with the output delivered as a complete `.tex` file plus a rendered PDF.
---

# Video Note Renderer

Use this skill to turn a Bilibili or YouTube video into a complete, compileable `.tex` note and a rendered PDF.

## Runtime Baseline

Use the following local stack by default:

- ASR: `faster-whisper` with `whisper-large-v3`
- OCR: `PaddleOCR` with `PP-OCRv5_server`

Runtime helpers live in `runtime/`:

- `setup_runtime.sh`
- `env.sh`
- `transcribe_with_faster_whisper.py`
- `run_ppocrv5.py`
- `merge_chunked_transcripts.py`

Start from this stack unless the current media demonstrably requires a different tool.

## Goal

Produce a professional Chinese lecture note from a video URL.

The output must:

- use the video's actual teaching or analytical content rather than subtitle text alone
- place the video's original cover image on the front page whenever available
- include all necessary high-value key frames as figures, without redundant screenshots
- end with a final synthesis section that includes the speaker's substantive closing discussion and your own distilled takeaways
- be structurally organized with `\section{...}` and `\subsection{...}`
- be a complete `.tex` document from `\documentclass` to `\end{document}`
- be compiled successfully to PDF as part of the final delivery

## Supported Platforms

### YouTube

- inspect title, duration, chapters, thumbnail, and subtitle tracks first
- prefer manual subtitles over auto subtitles
- prefer the best usable video source for figure extraction

### Bilibili

- inspect title, duration, thumbnail, and whether the video is multi-part
- detect 分P videos and ask which parts to process before downloading
- prefer CC subtitles when present
- if CC subtitles are absent, fall back to local speech-to-text via `faster-whisper`
- note that higher resolutions on Bilibili may require cookies
- do not use danmaku as a teaching source

## Source Acquisition

1. Inspect metadata first.
   Prefer title, chapters, duration, thumbnail availability, subtitle availability, and part structure before writing.

2. Acquire the original cover image before writing the `.tex`.
   Save it locally and reference that local file on the front page.

3. Acquire subtitles or speech-to-text.

   Subtitle priority:

   - YouTube manual subtitles
   - YouTube auto subtitles if no manual track is suitable
   - Bilibili CC subtitles
   - local speech-to-text using `runtime/transcribe_with_faster_whisper.py`

4. Prefer the best usable video file for frame extraction.

5. Keep source artifacts local when practical.
   Typical artifacts are metadata, cover image, transcript outputs, local video, extracted frames, and OCR results.

## Speech-to-Text

When subtitles are unavailable or insufficient, extract audio and transcribe locally.

```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 audio.wav -y
python runtime/transcribe_with_faster_whisper.py \
  audio.wav \
  --model large-v3 \
  --language zh \
  --device cuda \
  --batch-size 16 \
  --output-dir transcript
```

For long recordings, chunk the audio and merge later:

```bash
ffmpeg -i audio.wav -f segment -segment_time 1800 -c copy audio_chunks/chunk_%02d.wav -y
python runtime/transcribe_with_faster_whisper.py audio_chunks/chunk_00.wav --model large-v3 --language zh --device cuda --batch-size 16 --output-dir chunk_transcripts
python runtime/merge_chunked_transcripts.py chunk_transcripts --stem merged
```

## OCR

Use OCR to support frame selection and figure interpretation, not to replace the speaker's main line of reasoning.

```bash
python runtime/run_ppocrv5.py frames/ --device cpu --output-dir ocr-out
```

Use OCR especially for:

- charts
- tables
- slide bullets
- formulas
- overlays that explain the current visual state

Do not treat livestream overlays, gifts, or auto-generated meeting summaries as primary evidence unless the speaker explicitly relies on them.

## Teaching Content Rules

Build notes from:

- title and chapter structure when available
- the original cover image
- on-screen diagrams, formulas, tables, charts, and slides
- subtitle or ASR explanations
- code snippets shown or discussed

Skip or down-weight:

- greetings
- small talk
- sponsorship
- platform logistics
- repetitive audience interaction
- overlays, gifts, and summary widgets that do not add substantive analytical content

## Writing Rules

1. Write in Chinese unless the user asks for another language.

2. Reconstruct the teaching flow when needed; do not blindly mirror subtitle order.

3. Start from `assets/notes-template.tex`.

4. Put the original video cover on the front page when available.

5. Use figures whenever they materially improve explanation.

6. Do not place images inside custom message boxes.

7. When a mathematical formula appears:
   show it in `$$...$$`
   then immediately explain every symbol in a flat list

8. When code examples appear:
   wrap them in `lstlisting`
   include a descriptive `caption`

9. Use `importantbox`, `knowledgebox`, and `warningbox` only for high-signal teaching content.

10. End each major section with `\subsection{本章小结}`.

11. End the document with `\section{总结与延伸}`.

12. Do not emit `[cite]` placeholders in the LaTeX.

## Figure Handling

Select figures by teaching value, not by an arbitrary quota.

- use timestamped transcript segments as the main locator
- inspect dense candidate frames around the relevant span before picking one
- prefer the final readable state of a slide, chart, or build sequence
- include every figure necessary for clarity
- omit repetitive or low-information frames
- crop or isolate relevant regions when full-frame readability is poor

## Figure Time Provenance

Whenever the note references a specific video frame or crop derived from a frame, record its source time interval on the same page as a bottom footnote.

- show a concrete interval such as `00:12:31--00:12:46`
- use the transcript-aligned interval, not a vague chapter estimate
- keep the figure and footnote on the same page

## Delivery

Deliver all of the following:

- the final `.tex`
- the cover image referenced on the front page
- any extracted or generated figure assets referenced by the document
- the compiled PDF
- transcript outputs (`.srt` and `.json`) when local speech-to-text was used

When responding with final artifact locations:

- always include the local filesystem paths for the generated outputs
- if running inside WSL, also provide Windows File Explorer paths that can be opened directly, using `wslpath -w`
- for example, convert `/root/tmp/example/output.pdf` into a path such as `\\wsl.localhost\Ubuntu-22.04\root\tmp\example\output.pdf`
- prioritize the PDF and `.tex` paths, and include transcript or figure directories when they are part of the deliverable

## Asset

- `assets/notes-template.tex`: default LaTeX template to fill
