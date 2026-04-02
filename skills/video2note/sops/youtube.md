# YouTube 解析标准 SOP

本文档定义 `video2note` 在处理 YouTube 视频时的标准解析流程。主 Skill 文档只保留总规则；当输入来源为 YouTube 时，必须按本 SOP 执行。

## 适用范围

- `https://www.youtube.com/watch?...`
- `https://youtu.be/...`

## 目标

在开始写作前，稳定获取以下素材，并全部落盘到当前任务目录：

- 元数据 JSON
- 可用格式列表
- 字幕信息
- 原始封面图
- 用于抽帧的本地视频文件
- 必要时的音频或转录结果

## 任务目录约定

每次任务必须先创建独立任务目录，例如：

```bash
TASK_DIR="$VIDEO2NOTE_TMPDIR/20260402-150000-youtube"
mkdir -p "$TASK_DIR"/{metadata,cover,subtitles,source,frames,ocr,output}
```

建议目录结构：

```text
$TASK_DIR/
  metadata/
    info.json
    formats.txt
    subtitles.txt
  cover/
    cover.webp
  subtitles/
    manual.srt
    auto.srt
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

1. 识别 URL 为 YouTube
2. 探测元数据与格式
3. 保存字幕轨道信息
4. 下载原始封面图
5. 下载最匹配字幕
6. 下载最佳可用视频文件
7. 若字幕不可用，则转录本地媒体
8. 生成抽帧、OCR 与写作所需的本地素材

## 步骤 1：探测元数据

先只探测，不下载正片。

```bash
yt-dlp -j --skip-download "$URL" > "$TASK_DIR/metadata/info.json"
```

如需直接查看格式表：

```bash
yt-dlp -F "$URL" > "$TASK_DIR/metadata/formats.txt"
```

如需直接查看字幕表：

```bash
yt-dlp --print subtitles_table --print automatic_captions_table "$URL" > "$TASK_DIR/metadata/subtitles.txt"
```

### 验收标准

必须在 `metadata/info.json` 中确认至少这些信息：

- 标题
- 时长
- 章节信息是否存在
- 缩略图是否存在
- 字幕轨道是否存在
- 可用格式是否足够用于抽帧

### 字幕探测结果解释

- 若 `subtitles.txt` 中明确列出轨道，则按其结果继续处理
- 若输出为 `NA` / `NA`，默认按“当前探测结果未发现可用字幕”处理，而不是直接假设命令异常
- 若输出异常且与 `info.json` 明显矛盾，应重新探测一次，再决定是否转入 ASR 回退

## 步骤 2：下载原始封面图

若官方缩略图可用，应先下载原始封面图，而不是用视频帧替代。

```bash
yt-dlp --skip-download --write-thumbnail -o "$TASK_DIR/cover/cover.%(ext)s" "$URL"
```

### 封面处理规则

- 优先保留平台提供的原始缩略图
- 不要因为后续会抽帧，就跳过封面图下载
- 若下载出多个缩略图文件，优先选择分辨率最高、内容正常的一张作为首页封面

## 步骤 3：获取字幕

### 优先级 1：人工字幕

先尝试人工字幕：

```bash
yt-dlp --skip-download --write-subs --sub-langs "zh-Hans,zh-CN,zh,en.*" --convert-subs srt \
  -o "$TASK_DIR/subtitles/manual.%(ext)s" "$URL"
```

### 优先级 2：自动字幕

若人工字幕不可用，再尝试自动字幕：

```bash
yt-dlp --skip-download --write-auto-subs --sub-langs "zh-Hans,zh-CN,zh,en.*" --convert-subs srt \
  -o "$TASK_DIR/subtitles/auto.%(ext)s" "$URL"
```

### 字幕规则

- 人工字幕优先于自动字幕
- 优先选择与视频语言或用户要求最匹配的字幕轨道
- 只要后续还要做关键帧定位，就必须保留时间戳
- 不要在此阶段把字幕先整理成无时间戳纯文本

## 步骤 4：下载最佳可用视频文件

YouTube 必须先探测格式，再下载当前环境中实际可获取的最佳可用视频源。

常用命令模板：

```bash
yt-dlp -f "bestvideo+bestaudio/best" -o "$TASK_DIR/source/video.%(ext)s" "$URL"
```

若环境或带宽受限，可显式约束分辨率，例如：

```bash
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  -o "$TASK_DIR/source/video.%(ext)s" "$URL"
```

### 视频源选择规则

- 目标不是理论最高格式，而是当前环境里**能稳定下载**且适合抽帧的最佳格式
- 若分离流需要合并，允许使用 `bestvideo+bestaudio/...` 模式
- 下载完成后，应只保留最终用于抽帧和转录的本地视频文件路径

## 步骤 5：字幕不可用时的转录回退

若没有可用字幕，或字幕质量明显不足以支撑教学笔记，则对本地媒体做转录。

如果已有本地视频，可直接转录视频文件；也可先抽取音频：

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

- 本地视频必须先稳定落盘，再开始抽音频
- ASR 必须在 `audio.wav` 稳定落盘后再开始
- 不要把“下载视频 / 抽音频 / ASR”并行触发

### 回退规则

- 有高质量人工字幕时，不要优先做 ASR
- 自动字幕和人工字幕都不足时，再做 ASR
- 若视频语言并非中文，应按实际语言调整 `--language`

## 步骤 6：为抽帧和 OCR 做准备

后续抽帧、OCR、写作都以本地视频文件和带时间戳字幕为基础。

### 强制要求

- 关键帧定位优先基于带时间戳字幕或 ASR 片段
- 抽帧使用本地视频文件，不依赖在线播放页面
- OCR 只是补充，不能代替对帧内容的直接视觉检查

## 失败分支

### 情况 A：字幕有，但视频无法稳定下载

- 先保留元数据、字幕、封面图
- 再尝试降分辨率下载可用视频格式
- 只要能得到可用于抽帧的本地视频即可

### 情况 B：视频能下，但字幕完全不可用

- 直接转入 ASR 路径

### 情况 C：字幕不可用且 ASR 质量很差

- 先判断是否为 `CUDA out of memory`
- 若是 OOM，优先降低 `batch-size` 并继续坚持 GPU
- 仅当 ASR 质量本身不足时，才降级为视觉优先模式
- 视觉优先模式下，通过密集抽帧、OCR 补充和直接看图提取教学内容

## 最低交付前置素材

在开始写 `.tex` 之前，至少应具备以下之一：

- 封面图 + 高质量字幕 + 本地视频
- 封面图 + ASR 结果 + 本地视频
- 封面图 + 本地视频 + 纯视觉分析素材

若这三类条件都不满足，不应进入写作阶段。

## 输出命名与编译

- 主输出目录、`.tex` 和 PDF 应根据视频核心内容命名为 5-10 个中文字符的语义化短名
- 不要直接照抄平台原始长标题，也不要使用 `note`、`output`、`final` 之类弱语义名称
- 最终 PDF 默认使用 `xelatex` 或 `latexmk -xelatex` 编译，不要把 `pdflatex` 当作默认编译路径
