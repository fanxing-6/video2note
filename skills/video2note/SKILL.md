---
name: video2note
description: Generate a professional, figure-rich LaTeX course note and final PDF from a Bilibili, YouTube, TikTok, or Douyin lecture, tutorial, technical talk, analytical video, or livestream replay. Use when the user provides one of those video URLs and wants structured Chinese notes that combine the video's title, cover, key frames, charts, formulas, code, subtitle or speech-to-text explanations, and a final synthesis chapter, with the output delivered as a complete `.tex` file plus a rendered PDF.
---

# Video2Note

Use this skill to turn a Bilibili, YouTube, TikTok, or Douyin video into a complete, compileable `.tex` note and a rendered PDF.

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
- `resolve_dlpanda.py`

Start from this stack unless the current media demonstrably requires a different tool.

### Model Execution Policy

Any model-backed step should prefer GPU by default.

- Run Whisper on `--device cuda` whenever a usable GPU is present.
- Favor larger GPU batch sizes first and only back off if the runtime fails or runs out of memory.
- Prefer GPU for OCR when the runtime supports it.
- Only fall back to CPU when GPU is unavailable or demonstrably failing.

## Goal

Produce a professional Chinese lecture note from a video URL.

The output must:

- use the video's actual teaching or analytical content rather than transcript text alone
- place the video's original cover image on the front page whenever available
- include all necessary high-value key frames as figures, without redundant screenshots
- end with a final synthesis section that includes the speaker's substantive closing discussion and your own distilled takeaways
- be structurally organized with `\section{...}` and `\subsection{...}`
- be a complete `.tex` document from `\documentclass` to `\end{document}`
- be compiled successfully to PDF as part of the final delivery

## Pedagogical Standard

The notes must read like a strong human teacher is guiding the reader through the material.

- organize each major section so the reader first understands the motivation, then the main idea, then the mechanism, then the example or evidence, and finally the takeaway
- keep the logic continuous and the motivation explicit; make it clear why a concept appears, what problem it solves, and why the next idea follows
- aim for deep-but-accessible explanations: keep the technical depth, but introduce formalism only after giving intuition in plain language
- when a section is dense, break it into smaller subsections that progressively build understanding rather than compressing everything into one long derivation
- do not dump subtitle or ASR content in chronological order; rewrite it into a teaching sequence with clear intent, contrast, and buildup

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

### TikTok / Douyin

- do not make logged-in platform extraction the primary path
- resolve the share link through `runtime/resolve_dlpanda.py`
- fetch the `dlpanda` homepage, extract the hidden `t0ken`, request the result HTML, and parse the direct media links
- prefer the direct playable media URL from the result HTML over the website's proxy download endpoint
- use the downloaded local MP4 as the source for transcription and frame extraction

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
   - TikTok/Douyin local speech-to-text after resolving the direct video link
   - local speech-to-text using `runtime/transcribe_with_faster_whisper.py`

4. Prefer the best usable video file for frame extraction.

5. Keep source artifacts local when practical.
   Typical artifacts are metadata, cover image, transcript outputs, local video, extracted frames, OCR results, and resolved HTML for TikTok/Douyin when used.

## Long Video Strategy

For longer videos, do not rely on a single monolithic pass.

- If the video is longer than 20 minutes, or the subtitle / ASR file contains more than 300 subtitle entries, split the work into smaller segments.
- Prefer chapter boundaries for splitting. If chapters are unavailable or too uneven, split by coherent time windows or subtitle ranges.
- If the user explicitly asks for sub-agents and they are available, parallelize segment analysis with sub-agents; otherwise keep the segmentation local and integrate manually.
- Each segment analysis should return: the segment's teaching goal, the core claims, important formulas or code, required figures with time provenance, and any ambiguities that need integration-time resolution.
- Keep a small overlap between neighboring segments when the explanation crosses boundaries, then deduplicate during integration.
- The final PDF must read like one coherent note, not a concatenation of chunk summaries.

## Speech-to-Text

When subtitles are unavailable or insufficient, extract audio and transcribe locally.

```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 audio.wav -y
python runtime/transcribe_with_faster_whisper.py \
  audio.wav \
  --model large-v3 \
  --language zh \
  --device cuda \
  --batch-size 32 \
  --output-dir transcript
```

For long recordings, chunk the audio and merge later:

```bash
ffmpeg -i audio.wav -f segment -segment_time 1800 -c copy audio_chunks/chunk_%02d.wav -y
python runtime/transcribe_with_faster_whisper.py audio_chunks/chunk_00.wav --model large-v3 --language zh --device cuda --batch-size 32 --output-dir chunk_transcripts
python runtime/merge_chunked_transcripts.py chunk_transcripts --stem merged
```

## TikTok / Douyin Resolution

Use `runtime/resolve_dlpanda.py` when the source is TikTok or Douyin.

```bash
python runtime/resolve_dlpanda.py \
  "https://v.douyin.com/xxxxxxxx/" \
  --save-html dlpanda-result.html \
  --download-video input.mp4
```

The helper will:

- fetch `https://dlpanda.com/`
- extract the hidden `t0ken`
- request the resolved HTML result page
- parse the direct `video_url`, `audio_url`, proxy URL, and suggested filename
- optionally download the direct MP4 locally

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

For semantic understanding of frames:

- prefer direct visual inspection with the available image-viewing tool over OCR-only judgment
- do not treat OCR output as a substitute for actually checking what the frame shows
- use OCR to supplement figure extraction and reading, not to decide the full semantic meaning of a visual by itself

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
   Each section should answer, in order when applicable: what problem is being solved, why simpler views are insufficient, what the core idea is, how it works, and what the reader should retain.

3. Start from `assets/notes-template.tex`.

4. Put the original video cover on the front page when available.

5. Use figures whenever they materially improve explanation.

6. Do not place images inside custom message boxes.

7. When a mathematical formula appears:
   first explain in plain Chinese what the formula is trying to express and why it appears
   show it in `$$...$$`
   then immediately explain every symbol in a flat list

8. When code examples appear:
   explain the role of the code before the listing and summarize the expected behavior after it when useful
   wrap them in `lstlisting`
   include a descriptive `caption`

9. Use `importantbox`, `knowledgebox`, and `warningbox` only for high-signal teaching content.

10. End each major section with `\subsection{本章小结}`.

11. End the document with `\section{总结与延伸}`.

12. Do not emit `[cite]` placeholders in the LaTeX.

## Figure Handling

Select figures by teaching value, not by an arbitrary quota.

When locating candidate frames, bias strongly toward recall before precision.
It is better to inspect too many nearby candidates first than to miss the one frame where the slide, formula, table, or diagram is finally fully revealed and readable.

Frame understanding must come from direct visual inspection.

- Use the available image-viewing tool, such as `view image` when supported, to inspect candidate frames and crops before deciding what they show, how they should be described, and whether they are complete enough to include.
- Do not use OCR tools such as `tesseract` as a substitute for visual understanding of a frame.
- Do not infer a frame's semantic content only from nearby subtitles, filenames, OCR text, or timestamps without checking the image itself.
- Contact sheets, montages, and tiled strips are good for recall, but final keep-or-reject decisions and semantic naming must be based on actual image inspection.

### Frame Selection Checklist

Before inserting any video frame, inspect several nearby candidates from the same transcript-aligned interval and apply this checklist. If any item fails, reject the frame and keep searching nearby rather than forcing an approximate match.

- Relevance: the frame must directly support the exact concept discussed in the surrounding paragraph or subsection, not just the same broad topic.
- Required content visible: every visual element referenced in the text must already be visible in the frame.
- Fully revealed state: when slides, whiteboards, animations, or dashboards build progressively, use the final fully populated readable state rather than an intermediate state.
- Best nearby candidate: compare multiple nearby frames and prefer the one that is both most complete and most readable.
- Readability: text, formulas, labels, and diagram structure must be legible enough to justify inclusion.
- Crop opportunity: if irrelevant borders, UI chrome, subtitles, or decorative elements weaken clarity, crop the frame before inclusion.

### Frame Naming

- Use neutral timestamp-based names for raw candidate frames. Do not assign semantic names before inspecting the actual frame content.
- Rename a frame semantically only after visually confirming what is fully visible in the image.
- The semantic filename must describe the frame's actual visible content, not a guess based on subtitles, nearby narration, OCR text, or the intended paragraph topic.
- If the frame is partially revealed, transitional, or ambiguous, keep searching and do not lock in a semantic name yet.

- use timestamped transcript segments as the main locator
- inspect dense candidate frames around the relevant span before picking one
- prefer the final readable state of a slide, chart, or build sequence
- include every figure necessary for clarity
- omit repetitive or low-information frames
- crop or isolate relevant regions when full-frame readability is poor
- when a slide reveals content progressively, capture the final readable state and add intermediate frames only when they teach a genuinely different step
- prefer a sequence of necessary figures over one overloaded figure with unreadable labels
- preserve readability of formulas and labels

## Figure Time Provenance

Whenever the note references a specific video frame or crop derived from a frame, record its source time interval on the same page as a bottom footnote.

- show a concrete interval such as `00:12:31--00:12:46`
- use the transcript-aligned interval, not a vague chapter estimate
- keep the figure and footnote on the same page

## Visualization

Two acceptable routes:

- generate LaTeX-native visualizations with TikZ or PGFPlots
- generate figures ahead of time with scripts and include them as images

For script-generated illustrations, prefer Python tools such as `matplotlib` and `seaborn` when they are the clearest way to produce an accurate teaching figure.

When a visualization is generated externally rather than drawn natively in LaTeX:

- export the figure as `pdf` so it can be inserted into the `.tex` without rasterization loss
- prefer vector output for plots, charts, and schematic illustrations
- avoid `png` or `jpg` for script-generated teaching figures unless the content is inherently raster

Use visualizations for:

- process flows, pipelines, and architecture overviews
- curves and charts such as scaling laws, training curves, benchmark results, and ablation comparisons
- distributions, correlations, heatmaps, and other plots that explain data relationships
- complex functions, surfaces, contour plots, and geometric intuition figures
- tables or comparisons that become clearer when redrawn as charts
- summary diagrams that compress a section's core mechanism or takeaway into one figure

Do not add decorative graphics that do not teach anything.

## Final Checklist

Before delivery, verify all of the following:

- no important teaching content has been dropped, and no concrete but critical detail has been lost during condensation, restructuring, or summarization
- the text and figures are aligned: each inserted frame supports the surrounding explanation, necessary crops have been applied, and the chosen frame shows the fullest relevant information rather than a transitional or incomplete state
- the document is visually rich enough for teaching: check whether more high-information key frames should be added, and whether additional LaTeX-native or Python-script-generated illustrations would improve clarity

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
- derive the Windows path with `wslpath -w <linux_path>` rather than hand-writing it
- for example, convert `/root/tmp/example/output.pdf` into a path such as `\\wsl.localhost\Ubuntu-22.04\root\tmp\example\output.pdf`
- prioritize the PDF and `.tex` paths, and include transcript or figure directories when they are part of the deliverable

## Asset

- `assets/notes-template.tex`: default LaTeX template to fill
