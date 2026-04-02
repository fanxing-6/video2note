# TikTok / Douyin 解析标准 SOP

本文档定义 `video2note` 在处理 TikTok 或 Douyin 视频时的标准解析流程。主 Skill 文档只保留总规则；当输入来源为 TikTok / Douyin 时，必须按本 SOP 执行。

## 适用范围

- TikTok 分享链接或 canonical URL
- Douyin 分享链接或 canonical URL

## 目标

在开始写作前，稳定获取以下素材，并全部落盘到当前任务目录：

- 解析结果 JSON
- dlpanda 返回的 HTML
- 可直接使用的本地 MP4
- 必要时的本地音频
- ASR 结果
- 抽帧与 OCR 所需素材

## 任务目录约定

每次任务必须先创建独立任务目录，例如：

```bash
TASK_DIR="$VIDEO2NOTE_TMPDIR/20260402-150000-tiktok"
mkdir -p "$TASK_DIR"/{metadata,source,subtitles,frames,ocr,output}
```

建议目录结构：

```text
$TASK_DIR/
  metadata/
    dlpanda.json
    dlpanda-result.html
  source/
    input.mp4
    audio.wav
  subtitles/
    input.srt
    input.json
  frames/
  ocr/
  output/
    note.tex
    note.pdf
```

## 前置条件

在执行平台解析前，必须先准备**用户级运行时环境**。

- 真实运行时目录：`VIDEO2NOTE_HOME`
- 任务输出目录：`VIDEO2NOTE_TMPDIR`
- 脚本源码目录：`VIDEO2NOTE_RUNTIME_SCRIPTS_DIR`

若尚未初始化运行时，应使用运行时脚本源码目录中的脚本进行初始化，例如：

```bash
bash <runtime-scripts-dir>/setup_runtime.sh
source <runtime-scripts-dir>/env.sh
```

注意：

- `runtime/` 只是脚本源码目录，不是第二套运行时目录
- 不要把 skill 安装目录当作真实运行时目录使用

## SOP 总览

1. 识别 URL 为 TikTok / Douyin
2. 不把需要登录的平台提取作为主路径
3. 使用 `resolve_dlpanda.py` 解析
4. 保存 dlpanda 返回的 HTML 和解析 JSON
5. 下载直链 MP4 到本地
6. 对本地 MP4 做 ASR
7. 基于本地 MP4 做抽帧和 OCR

## 步骤 1：通过 `resolve_dlpanda.py` 解析

标准命令：

```bash
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/resolve_dlpanda.py" \
  "$URL" \
  --save-html "$TASK_DIR/metadata/dlpanda-result.html" \
  --download-video "$TASK_DIR/source/input.mp4" \
  > "$TASK_DIR/metadata/dlpanda.json"
```

该脚本会：

- 获取 `https://dlpanda.com/`
- 提取隐藏字段 `t0ken`
- 请求解析结果 HTML
- 从 HTML 中提取 `video_url`、`audio_url`、`proxy_url` 和建议文件名
- 若提供 `--download-video`，则直接下载解析出的 MP4

## 步骤 2：检查解析结果

在 `metadata/dlpanda.json` 中至少确认：

- `input_url`
- `result_url`
- `video_url`
- `audio_url`
- `proxy_url`
- `filename`

### 解析结果规则

- 优先使用结果 HTML 中解析出的**可直接播放媒体 URL**
- 不要优先依赖网站代理下载端点
- 若 `video_url` 存在，应直接将其下载到本地并作为后续唯一主视频源

## 步骤 3：转录本地 MP4

解析完成后，以本地 MP4 作为转录源。

可先抽取音频：

```bash
ffmpeg -i "$TASK_DIR/source/input.mp4" -ar 16000 -ac 1 "$TASK_DIR/source/audio.wav" -y
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/transcribe_with_faster_whisper.py" \
  "$TASK_DIR/source/audio.wav" \
  --model large-v3 \
  --language zh \
  --device cuda \
  --batch-size 8 \
  --output-dir "$TASK_DIR/subtitles"
```

执行边界：

- 直链 MP4 必须先稳定落盘，再开始抽音频
- ASR 必须在 `audio.wav` 稳定落盘后再开始
- 不要把“下载 MP4 / 抽音频 / ASR”并行触发

## 步骤 4：为抽帧和 OCR 做准备

TikTok / Douyin 的后续抽帧、OCR、写作都必须以本地 MP4 为基础。

### 抽帧与 OCR 规则

- 不要依赖在线页面截图作为主素材来源
- 应优先对本地 MP4 抽帧，再结合 OCR 和直接视觉检查
- OCR 只是辅助，不代替对实际帧内容的理解

## 失败分支

### 情况 A：解析成功但没有直链 `video_url`

- 记录解析 JSON 和 HTML
- 检查是否仅拿到 `proxy_url`
- 若没有可直接使用的视频源，不应继续写作阶段

### 情况 B：直链下载失败

- 先保留解析 JSON 和 HTML
- 再判断是否还有可用 `audio_url` 或其他媒体路径
- 若没有可用本地媒体文件，不应继续转录和抽帧

### 情况 C：视频下载成功但音频质量差

- 仍优先尝试 ASR
- 若出现 `CUDA out of memory`，优先降低 `batch-size`，继续坚持 GPU
- 若 ASR 质量本身不足，再提高视觉分析权重

## 最低交付前置素材

在开始写 `.tex` 之前，至少应具备以下素材：

- 解析 JSON
- dlpanda HTML
- 本地 MP4
- ASR 结果或足够支撑分析的视觉素材

若没有本地 MP4，不应进入写作阶段。

## 输出命名与编译

- 主输出目录、`.tex` 和 PDF 应根据视频核心内容命名为 5-10 个中文字符的语义化短名
- 不要直接照抄平台原始长标题，也不要使用 `note`、`output`、`final` 之类弱语义名称
- 最终 PDF 默认使用 `xelatex` 或 `latexmk -xelatex` 编译，不要把 `pdflatex` 当作默认编译路径
