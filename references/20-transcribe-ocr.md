# 20 Transcribe/OCR

在生成文本轨、OCR 或关键帧前读取本卡片。目标是形成可定位、可复核的证据层。

## 输入

- `metadata/source.json`
- 本地视频或平台字幕
- `cover/`
- 可选关键帧、contact sheet

## 输出

- `subtitles/raw.srt`
- 可选：`subtitles/clean.srt`
- 可选：`subtitles/transcript.json`
- 可选：`frames/contact_sheet.png`
- 可选：`ocr/`

## 字幕与 ASR

- 优先平台 CC 字幕。
- 无 CC 或字幕质量不足时，抽音频并使用本地 `faster-whisper large-v3`。
- 长音频先分块转录，再合并。
- `raw.srt` 是证据轨，永远不覆盖、不删除。
- `clean.srt` 只允许字幕级纠错、删除语气词、必要断句和轻量停顿空格，不得书面化改写、总结或扩写。
- 若生成 `clean.srt`，必须运行 `runtime/check_clean_srt.py`。

## 视觉素材与 OCR

- 对视频帧的理解必须来自直接视觉检查，不允许只根据字幕或 OCR 猜图。
- contact sheet 用于高召回初筛，最终选帧必须检查实际图片。
- OCR 是辅助，不替代视觉检查。
- 纯视觉模式下，应提高抽帧密度，保留能支撑教学内容的截图、图表、公式、代码或幻灯片。

## 硬规则

- `ffmpeg` 命令使用 `-nostdin`。
- ASR 默认 GPU；OOM 降低 batch size 后重试。
- 如果音频、字幕、视觉素材都不足以支撑报告，停止进入写作。
- 更新 `metadata/source.json` 中的 `text_artifacts`, `primary_text_artifact`, `raw_text_artifact`, `visual_artifacts`。

## 门禁

- 有可用证据轨：文本轨或纯视觉证据。
- `source.json` 已指向实际存在的证据文件。
- stage ledger 已记录字幕来源、ASR 模型、GPU/CPU 状态、OCR/抽帧状态。
