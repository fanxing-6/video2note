# Bilibili 解析标准 SOP

本文档定义 `video2note` 在处理 Bilibili 视频时的标准解析流程。主 Skill 文档只保留总规则；当输入来源为 Bilibili 时，必须按本 SOP 执行。

## 适用范围

- `https://www.bilibili.com/video/BV...`
- `https://b23.tv/...`

## 目标

在开始写作前，稳定获取以下素材，并全部落盘到当前任务目录：

- 元数据 JSON
- 可用格式列表
- 字幕信息
- 原始封面图
- 用于抽帧的本地视频文件
- 必要时的音频或转录结果
- 若为分 P 视频，明确用户选择的分 P 范围

## 任务目录约定

每次任务必须先创建独立任务目录，例如：

```bash
TASK_DIR="$VIDEO2NOTE_TMPDIR/20260402-150000-bilibili"
mkdir -p "$TASK_DIR"/{metadata,cover,subtitles,source,frames,ocr,output}
```

建议目录结构：

```text
$TASK_DIR/
  metadata/
    info.json
    formats.txt
    subtitles.txt
    parts.txt
  cover/
    cover.webp
  subtitles/
    cc.srt
    transcript.srt
    transcript.json
  source/
    video.mp4
    audio.wav
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

1. 识别 URL 为 Bilibili
2. 探测元数据、格式和字幕
3. 检测是否为分 P 视频
4. 让用户明确分 P 选择
5. 下载原始封面图
6. 先尝试 CC 字幕
7. 若无 CC，则转入本地 `faster-whisper`
8. 若 ASR 路径仍不可用，则转入纯视觉模式
9. 下载最佳可用视频文件
10. 生成抽帧、OCR 与写作所需的本地素材

## 步骤 1：探测元数据

先只探测，不下载正片。

```bash
yt-dlp -j --skip-download "$URL" > "$TASK_DIR/metadata/info.json"
```

查看格式表：

```bash
yt-dlp -F "$URL" > "$TASK_DIR/metadata/formats.txt"
```

查看字幕表：

```bash
yt-dlp --print subtitles_table --print automatic_captions_table "$URL" > "$TASK_DIR/metadata/subtitles.txt"
```

### 验收标准

必须在 `metadata/info.json` 中确认至少这些信息：

- 标题
- 时长
- 缩略图是否存在
- 字幕是否存在
- 是否包含分 P 结构
- 可用视频格式是否足够用于抽帧

### 字幕探测结果解释

- 若 `subtitles.txt` 中明确列出轨道，则按其结果继续处理
- 若输出为 `NA` / `NA`，默认按“当前探测结果未发现可用字幕”处理，而不是直接假设命令异常
- 若输出异常且与 `info.json` 明显矛盾，应重新探测一次，再决定是否转入 ASR 回退

## 步骤 2：识别分 P 并询问用户

若探测结果表明是分 P 视频，必须先列出所有分 P，再询问用户处理范围。

### 分 P 处理规则

- 不要在未明确分 P 范围前直接全量下载
- 分 P 是一等结构信息，不应简单忽略
- 长视频拆分时，也应优先按分 P 边界组织分析

可将分 P 信息整理到：

```bash
$TASK_DIR/metadata/parts.txt
```

## 步骤 3：下载原始封面图

若官方缩略图可用，应先下载原始封面图，而不是用视频帧替代。

```bash
yt-dlp --skip-download --write-thumbnail -o "$TASK_DIR/cover/cover.%(ext)s" "$URL"
```

## 步骤 4：字幕三级回退

### 优先级 1：平台 CC 字幕

先尝试平台 CC 字幕：

```bash
yt-dlp --skip-download --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt \
  -o "$TASK_DIR/subtitles/cc.%(ext)s" "$URL"
```

### 字幕规则

- 优先使用平台内嵌 CC 字幕
- 字幕语言优先尝试 `zh-Hans`、`zh-CN`、`zh`、`ai-zh`
- 在仍需定位关键帧时，必须保留时间戳

### 优先级 2：本地 `faster-whisper`

若没有可用 CC 字幕，则先获取本地媒体，再做 ASR。

可先抽取音频：

```bash
ffmpeg -i "$TASK_DIR/source/video.mp4" -ar 16000 -ac 1 "$TASK_DIR/source/audio.wav" -y
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/transcribe_with_faster_whisper.py" \
  "$TASK_DIR/source/audio.wav" \
  --model large-v3 \
  --language zh \
  --device cuda \
  --batch-size 8 \
  --output-dir "$TASK_DIR/subtitles"
```

执行边界：

- `ffmpeg` 抽取音频必须在本地视频稳定落盘后再开始
- ASR 必须在 `audio.wav` 稳定落盘后再开始
- 不要把“下载视频 / 抽音频 / ASR”并行触发

### 优先级 3：纯视觉模式

若音频质量过差、语音不清晰、背景噪声过重，或 ASR 结果不足以支撑教学笔记，则转入纯视觉模式。

### 纯视觉模式规则

- 不再依赖字幕作为主线来源
- 改为依赖密集抽帧、直接视觉检查和 OCR 补充提取教学内容
- 不要因为没有字幕就放弃整段内容；应优先保留屏幕上确实存在的教学材料

## 步骤 5：下载最佳可用视频文件

常用命令模板：

```bash
yt-dlp -f "bestvideo+bestaudio/best" -o "$TASK_DIR/source/video.%(ext)s" "$URL"
```

若需要浏览器 Cookie 以获取 1080P+：

```bash
yt-dlp --cookies-from-browser chrome -f "bestvideo+bestaudio/best" \
  -o "$TASK_DIR/source/video.%(ext)s" "$URL"
```

### 视频源选择规则

- 目标不是理论最高格式，而是当前环境里**能稳定下载**且适合抽帧的最佳格式
- Bilibili 的 1080P+ 视频通常需要浏览器 Cookie
- 若用户未提供可用 Cookie，允许先降级到可公开下载的较低分辨率版本，以保证流程继续

## 步骤 6：为抽帧和 OCR 做准备

后续抽帧、OCR、写作都以本地视频文件和带时间戳字幕或转录结果为基础。

### 强制要求

- 关键帧定位优先基于带时间戳字幕或 ASR 片段
- 纯视觉模式下，必须通过密集抽帧和直接视觉检查补足信息
- 弹幕不作为教学内容来源
- OCR 只是辅助，不代替对画面的直接理解

## 失败分支

### 情况 A：探测到分 P，但用户未指定范围

- 先停止下载主视频
- 先回到用户确认分 P 选择

### 情况 B：没有 CC 字幕

- 转入本地 `faster-whisper`

### 情况 C：ASR 结果很差

- 先判断是否为 `CUDA out of memory`
- 若是 OOM，优先降低 `batch-size` 并继续坚持 GPU
- 只有在 ASR 质量本身不足时，才转入纯视觉模式

### 情况 D：1080P+ 下载失败

- 尝试 `--cookies-from-browser chrome`
- 若仍失败，则回退到当前环境可稳定下载的较低分辨率版本

## 最低交付前置素材

在开始写 `.tex` 之前，至少应具备以下之一：

- 封面图 + CC 字幕 + 本地视频
- 封面图 + ASR 结果 + 本地视频
- 封面图 + 本地视频 + 纯视觉分析素材

若这三类条件都不满足，不应进入写作阶段。

## 输出命名与编译

- 主输出目录、`.tex` 和 PDF 应根据视频核心内容命名为 5-10 个中文字符的语义化短名
- 不要直接照抄平台原始长标题，也不要使用 `note`、`output`、`final` 之类弱语义名称
- 最终 PDF 默认使用 `xelatex` 或 `latexmk -xelatex` 编译，不要把 `pdflatex` 当作默认编译路径
