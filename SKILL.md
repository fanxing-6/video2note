---
name: video2note
description: 根据用户提供的 Bilibili、YouTube、TikTok 或 Douyin 等视频内容，生成一份专业、结构化的中文 LaTeX 笔记及最终 PDF。
---
# Video2Note

使用本 Skill 将视频内容转换为一份完整、可编译的 `.tex` 笔记及渲染后的 PDF。

支持路径聚焦在 Bilibili、YouTube、TikTok 和 Douyin 视频。主流程先做平台识别与视频素材采集，再把字幕、ASR、关键帧、封面和必要的 OCR 结果整理为视频内容包，最后生成中文 LaTeX/PDF 笔记。

## 运行时基线

默认使用以下本地技术栈：

- **ASR（自动语音识别）**：`faster-whisper`，模型 `whisper-large-v3`
- **OCR（光学字符识别）**：`PaddleOCR`，模型 `PP-OCRv5_server`

Skill 自带的运行时辅助脚本源码位于 `runtime/` 目录下：

- `setup_runtime.sh`
- `env.sh`
- `transcribe_with_faster_whisper.py`
- `run_ppocrv5.py`
- `merge_chunked_transcripts.py`
- `resolve_dlpanda.py`
- `check_clean_srt.py`

目录职责必须严格区分：

- `runtime/`：只表示脚本源码目录
- `VIDEO2NOTE_HOME`：唯一真实共享运行时目录
- `VIDEO2NOTE_TMPDIR`：任务产出根目录

默认目录约定如下：

- 共享运行时根目录：`$HOME/video2note`；若当前 shell 未设置 `HOME`，则回退到 `$USERPROFILE/video2note`
- 共享虚拟环境：`$VIDEO2NOTE_HOME/.venv`
- 任务产出根目录：`${TMPDIR:-/tmp}/video2note`；若 `TMPDIR` 不存在，则回退到 `${TEMP}`、`${TMP}` 或 `/tmp/video2note`
- 每次任务都应在 `VIDEO2NOTE_TMPDIR` 下创建独立子目录，避免互相覆盖

除非当前媒体明确需要其他工具，否则请从上述技术栈开始。

### 模型执行策略

任何依赖模型的步骤都应默认优先使用 GPU：

- 只要 GPU 路径已经准备完整，Whisper 转录必须优先在 `--device cuda` 上运行。
- “较大的 GPU 批大小优先”表示探索顺序，而不是固定默认值；对真实长音频，稳定值依赖显存、模型和音频长度。
- 默认应从更保守的 GPU `batch-size` 起步，再逐步上探，而不是把 `32` 当作稳定基线。
- 若遇到 `CUDA out of memory`，优先降低 `batch-size`，继续坚持 GPU，而不是立即回退 CPU。
- 若遇到 `libcublas`、`libcudnn`、`nvrtc` 等 CUDA 库缺失，应先补齐共享运行时依赖，再重试 GPU 路径。
- OCR 在运行时支持的情况下也应优先使用 GPU。
- 仅在 GPU 不可用或明确出现故障时，才回退到 CPU。

## 视频平台与 SOP 路由

主文档只定义视频笔记的统一契约，不展开各平台的具体采集步骤。
在开始处理之前，先判断视频来自哪个平台，再跳转到对应 SOP 文档。

### SOP 列表

- YouTube：查看 `sops/youtube.md`
- Bilibili：查看 `sops/bilibili.md`
- TikTok / Douyin：查看 `sops/tiktok-douyin.md`

后续扩展的视频平台 SOP 也应遵循同一主契约，不要把多个平台的具体采集细节混写在当前主文档中。

## 视频内容包

不同视频平台在进入写作与渲染阶段之前，应先被整理为同一份规范化视频内容包。推荐在任务目录中落盘为：

```text
$TASK_DIR/metadata/source.json
```

推荐的最小字段集合包括：

- `source_kind`：`video`
- `title`
- `author`
- `publish_date`
- `source_url`
- `hero_asset_path`
- `duration`
- `text_artifacts[]`
- `primary_text_artifact`
- `raw_text_artifact`
- `clean_text_artifact`
- `coverage_review_path`
- `visual_artifacts[]`
- `locator_type`：`time_range`

该内容包的目标是解耦：

- 上游平台适配器负责采集与规范化
- 下游笔记生成器负责基于视频内容包写作与渲染

不要让写作层直接耦合 YouTube、Bilibili、TikTok 或 Douyin 的平台采集细节。

## 目标

根据源视频生成一份专业、结构化的中文讲座笔记或主题笔记。

输出必须满足以下要求：

- 基于源视频的实际教学、分析或论证内容，而非仅机械堆砌字幕或 ASR 文本
- 在存在高价值封面或头图时，将其放在首页
- 在存在高价值视觉素材时，包含必要的关键帧、配图、图表或重绘插图，避免冗余截图
- 以最终综合章节收尾，涵盖来源中的实质性总结讨论以及你自己提炼的核心要点
- 结构上使用 `\section{...}` 和 `\subsection{...}` 进行组织
- 从 `\documentclass` 到 `\end{document}` 构成一份完整的 `.tex` 文档
- 作为最终交付物的一部分，必须成功编译为 PDF

## 教学标准

笔记的阅读体验应当像一位优秀的教师在引导读者学习材料。

- 每个主要章节的组织顺序为：先讲动机，再讲核心思想，然后是机制原理，接着是示例或证据，最后是总结要点
- 保持逻辑连贯、动机明确；清楚说明一个概念为何出现、它解决了什么问题、以及下一个概念为何随之而来
- 追求“深入但易懂”的解释：保留技术深度，但仅在给出直观的白话解释之后才引入形式化表达
- 当某一节内容密集时，将其拆分为更小的子节，逐步建立理解，而不是把所有内容压缩进一个冗长的推导中
- 不要按时间顺序堆砌字幕或 ASR 内容；将其重写为具有明确意图、对比和递进关系的教学序列

## 支持的视频平台

视频输入覆盖以下平台：

### YouTube

- 支持 `youtube.com/watch` 与 `youtu.be` 短链接
- 具体解析流程必须查看 `sops/youtube.md`

### Bilibili

- 支持 `bilibili.com/video/BV...` 与 `b23.tv` 短链接
- 具体解析流程必须查看 `sops/bilibili.md`

### TikTok / Douyin

- 具体解析流程必须查看 `sops/tiktok-douyin.md`

## 源文件获取总规则

1. **首先检查元数据**
   在动笔之前，优先获取标题、作者、发布日期、时长信息、章节结构、封面可用性，以及字幕可用性。
2. **在编写 `.tex` 之前获取高价值头图或封面**
   若视频存在原始封面、节目封面或其他高价值头图，应优先落盘，并在首页引用该本地文件。
3. **获取主文本证据**
   优先使用平台字幕，其次从视频音轨进行 ASR。
4. **优先获取后续分析真正需要的原始素材**
   优先获取最佳可用本地视频文件、封面、关键帧、章节信息和与讲解对齐的字幕或 ASR 结果。
5. **在可行的情况下将源文件保存在任务目录。**
   任务目录应位于 `VIDEO2NOTE_TMPDIR` 下的独立子目录中。
6. **在进入写作阶段前，先整理视频内容包。**
   写作层优先消费 `metadata/source.json`，而不是直接耦合某个特定视频平台的原始采集结果。

## 字幕双轨策略

当平台字幕或 ASR 结果可用时，应同时保留原始证据轨和清洗阅读轨。

- `subtitles/raw.srt`：原始字幕或 ASR SRT 的规范化副本，永远不覆盖、不删除，作为时间脚注、证据核查和 coverage review 的主依据。
- `subtitles/clean.srt`：可选清洗轨，用于写作阅读和短对话摘录。只允许字幕级纠错、删除无意义语气词、必要断句和轻量停顿空格；不要书面化改写、总结、扩写或跨条补词。
- `subtitles/transcript.json`：若转录脚本生成结构化结果，应与 SRT 一起保留。
- 若生成 `clean.srt`，必须运行 `python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/check_clean_srt.py" "$TASK_DIR/subtitles/raw.srt" "$TASK_DIR/subtitles/clean.srt"`；有告警时人工复核，不能把脚本通过当作音频级精听。
- 若当前任务进入纯视觉模式，不要强造 `clean.srt`；在 `metadata/source.json` 中记录没有可用文本轨，并提高视觉素材和 OCR 补充的权重。

进入写作阶段前，`metadata/source.json` 应尽量记录：

```json
{
  "text_artifacts": ["subtitles/raw.srt", "subtitles/clean.srt", "subtitles/transcript.json"],
  "primary_text_artifact": "subtitles/clean.srt",
  "raw_text_artifact": "subtitles/raw.srt",
  "clean_text_artifact": "subtitles/clean.srt",
  "coverage_review_path": "output/coverage_review.md"
}
```

写作层默认读取 `primary_text_artifact`；涉及事实核查、时间区间、漏召回审查或争议性摘录时，回到 `raw_text_artifact`。

## 长视频策略

对于较长视频，不要依赖单次整体性遍历。

- 若视频时长超过 20 分钟，或字幕 / ASR 条目超过 300 条，则将工作拆分为更小的片段。
- 对于 Bilibili 多 P 视频，仍应优先按分 P 边界拆分。
- 若边界信息不可用或分布不均，则按合理的时间窗口或字幕范围拆分。
- 若用户明确要求使用子代理（sub-agents）且环境支持，可并行分析各片段；否则在本地完成分段并手动整合。
- 每个片段的分析应返回：该片段的教学目标、核心论点、重要公式或代码、所需插图及其对应来源定位，以及整合时需要解决的歧义。
- 当解释跨越边界时，让相邻片段保持少量重叠，然后在整合阶段去重。
- 最终 PDF 必须读起来像一篇连贯的笔记，而不是各片段摘要的简单拼接。

## 语音转文字

当字幕不可用或不够充分时，提取视频音轨并在本地进行转录。

```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 audio.wav -y
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/transcribe_with_faster_whisper.py" \
  audio.wav \
  --model large-v3 \
  --language zh \
  --device cuda \
  --batch-size 8 \
  --output-dir "$TASK_DIR/transcript"
```

转录前必须先确保输入视频已经稳定落盘，不要把“下载视频”和“转 wav + ASR”并行触发。

对于较长的视频音轨，先分块处理再合并：

```bash
ffmpeg -i audio.wav -f segment -segment_time 1800 -c copy audio_chunks/chunk_%02d.wav -y
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/transcribe_with_faster_whisper.py" audio_chunks/chunk_00.wav --model large-v3 --language zh --device cuda --batch-size 8 --output-dir "$TASK_DIR/chunk_transcripts"
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/merge_chunked_transcripts.py" "$TASK_DIR/chunk_transcripts" --stem merged
```

## OCR

使用 OCR 来辅助图片解读，而不是取代源内容本身的主要论证逻辑。

```bash
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/run_ppocrv5.py" frames/ --device cpu --output-dir "$TASK_DIR/ocr-out"
```

OCR 特别适用于以下场景：

- 图表
- 表格
- 幻灯片要点
- 公式
- 视频画面中的关键文字
- 解释当前视觉状态的叠加图层

请勿将直播叠加图层、礼物特效或自动生成的会议摘要作为主要证据，除非源内容明确依赖它们。

对于视觉素材的语义理解：

- 优先使用可用的图像查看工具直接检查图片、帧或裁剪区域，而非仅依赖 OCR 判断
- 不要将 OCR 输出视为实际查看视觉素材的替代品
- 使用 OCR 作为插图提取和阅读的补充手段，而不是单独用它来决定视觉内容的完整语义

## 教学内容规则

笔记内容应基于以下素材构建：

- 标题和章节结构（如有）
- 原始封面图或高价值头图
- 视频帧、示意图、公式、表格、图表和幻灯片
- 字幕或 ASR 讲解
- 展示或讨论的代码片段

以下内容应跳过或降低权重：

- 问候和寒暄
- 闲聊
- 赞助内容
- 平台后勤信息
- 重复性的观众互动
- 对实质性分析内容没有贡献的叠加图层、礼物特效和总结挂件

## 写作规则

1. 除非用户要求其他语言，否则使用中文撰写。
2. 在需要时重构教学流程；不要盲目照搬字幕顺序。
   每个章节在适用情况下应按以下顺序回答：正在解决什么问题、为什么更简单的视角不够、核心思想是什么、如何运作、以及读者应记住什么。
   避免滥用“不是……而是……”句式；只有当源视频确实建立了有助于理解机制的关键对比时才使用。
   不要使用空泛抽象表达。主张应尽量落到具体机制、例子、变量、步骤、观察现象、时间戳、图片或讲者证据上。
3. 以 `assets/notes-template.tex` 为起点。
   该模板已统一提供封面、目录、正文页码、页眉页脚和 `lstlisting` 代码块样式；除非确有必要，不要在生成结果中重新定义这些基础排版规则。
4. 在可用时，将原始封面或头图放在首页。
5. 当图片能够实质性提升解释效果时，使用插图。
6. 不要将图片放置在自定义消息框内。
7. 当出现数学公式时：
   先用中文白话解释该公式试图表达什么以及它为何出现
   然后在 `$$...$$` 中展示公式
   紧接着用平铺列表解释每个符号的含义
8. 当出现代码示例时：
   在代码清单之前解释代码的作用，之后如有需要总结预期行为
   将其包裹在 `lstlisting` 环境中
   添加描述性的 `caption`
   代码块应尽量保持聚焦，避免一次贴入过长原始代码；优先保留最能支撑讲解的核心片段
   对长行友好的换行、行号、背景色和边框样式由模板统一提供，不要在正文中额外手工覆盖
9. 有意识地使用 `importantbox`、`knowledgebox` 和 `warningbox` 来承载高价值教学信号。

   - `importantbox` 用于读者必须带走的核心概念、关键结论、机制摘要、关键步骤或稠密内容后的压缩重述
   - `knowledgebox` 用于改善理解但不属于主线的背景知识，如前置知识、历史脉络、术语对比、工程上下文、设计权衡和直觉类比
   - `warningbox` 用于常见误解、隐藏前提、易错实现点、错误直觉与正确直觉的对照
   - `dialoguebox` 只用于访谈、圆桌、播客或强对话视频中的短原话片段；当原话本身比概括更有临场感、幽默、追问张力或直觉价值时使用
   - `dialoguebox` 必须保留说话人标签和具体时间区间，可包含一个问答或数个紧密相连的澄清/反驳/补充回合；轻微修正 ASR 错字可以，但不要改写为书面表达
   - 不要把问候、寒暄、长字幕块、普通解释或可以更清楚概括的内容放进 `dialoguebox`
   - 不存在“每章一个 box”的配额；只有在内容真正承载清晰教学信号时才使用
   - box 应尽量紧跟触发它的段落、推导或示例，而不是孤立堆放
   - 常规叙述应保持普通正文；box 用于高信噪比要点，而不是装饰
   - 图片必须放在 `importantbox`、`knowledgebox`、`warningbox` 和 `dialoguebox` 之外
10. 每个主要章节以 `\subsection{本章小结}` 收尾。
    当确实存在一到两个高价值外部链接时，可额外添加 `\subsection{拓展阅读}`。
11. 文档以 `\section{总结与延伸}` 结束。
    该节必须尽可能包含：
    - 演讲者在收尾阶段给出的实质性总结，而不是礼貌性结束语
    - 你对核心论点、机制和实践含义的结构化提炼
    - 跨章节的综合归纳、概念压缩和必要的交叉关联
    - 当材料支持时，给出可执行的 takeaway、开放问题或后续思考方向

12. 不要在 LaTeX 中输出 `[cite]` 占位符。

## 图片处理

根据教学价值选择插图，而非套用任意配额。

对于视频输入，在定位候选帧时，前期应强烈偏向召回率（recall）而非精确率（precision）。
宁可先检查过多附近的候选帧，也不要错过幻灯片、公式、表格或示意图最终完整呈现且清晰可读的那一帧。

视觉素材的理解必须来自直接的视觉检查。

- 使用可用的图像查看工具（如支持的 `view image`）在决定图片、帧或裁剪区域的内容、描述方式以及完整度是否足够之前，先直接检查图像本身
- 不要用 OCR 工具（如 `tesseract`）替代对视觉素材的理解
- 不要仅根据附近的字幕、文件名、OCR 文本、段落主题或时间戳来推断图像语义，而不亲自查看图片本身
- 联系表（contact sheets）、蒙太奇和拼贴条带有助于提高召回率，但最终的去留决定和语义命名必须基于对实际图像的检查

### 视频帧选择检查清单

在插入任何视频帧之前，从同一转录对齐区间中检查多个附近的候选帧，并应用以下检查清单。若有任何一项未通过，则拒绝该帧并继续在附近搜索，而不是强行凑合。

- **相关性**：该帧必须直接支持周围段落或子节讨论的**确切**概念，而非仅仅是同一宽泛主题。
- **必要内容可见**：文本中引用的每个视觉元素都必须在帧中已经可见。
- **完全呈现状态**：当幻灯片、白板、动画或仪表板逐步构建时，使用最终完全填充且可读的状态，而非中间过渡状态。
- **附近最佳候选**：对比多个附近的帧，优先选择既最完整又最清晰的帧。
- **可读性**：文字、公式、标签和图表结构必须足够清晰，以证明其值得被包含。
- **裁剪机会**：如果无关边框、UI 外壳、字幕或装饰性元素削弱了清晰度，则在插入前裁剪帧。

### 视频帧命名

- 对原始候选帧使用基于时间戳的中性命名。在检查实际帧内容之前，不要赋予语义名称。
- 仅在通过视觉确认图像中完全可见的内容后，才对帧进行语义重命名。
- 语义文件名必须描述帧的实际可见内容，而非基于字幕、附近旁白、OCR 文本或预期段落主题的猜测。
- 如果帧是部分呈现的、过渡性的或存在歧义的，继续搜索，暂时不要确定语义名称。
- 以带时间戳的转录片段作为主要定位依据。
- 在相关时间跨度周围检查密集的候选帧，然后再挑选。
- 优先获取幻灯片、图表或构建序列的最终可读状态。
- 包含所有对清晰度必要的插图。
- 省略重复或信息含量低的帧。
- 当整帧可读性较差时，裁剪或隔离相关区域。
- 当幻灯片逐步呈现内容时，捕获最终可读状态；仅当中间帧真正教授了不同的步骤时，才添加中间帧。
- 优先使用一系列必要的插图，而非塞满不可读标签的单一超载图片。
- 保持公式和标签的可读性。

## 图片来源定位

每当笔记引用某个特定的视觉素材时，应在附近明确记录其来源定位。

- 对视频帧或由其裁剪而来的图片，在同一页底部以脚注形式记录来源时间区间，例如 `00:12:31--00:12:46`
- 对字幕、旁白或 ASR 片段引用，优先使用与视频转录对齐的时间区间，而不是模糊的章节估算
- 如果图片是从视频帧裁剪得到，脚注仍然应指向原始视频时间区间
- 如果同一张图中的多个附近帧都来自同一转录区间，一个清晰脚注即可
- 将图片和脚注保持在同一页；必要时优先使用更稳定的排版方式，避免浮动体把两者拆开

## 可视化

对于仅靠截图和正文仍然难以讲清的概念，应补充准确的可视化。

两种可接受的路线：

- 使用 TikZ 或 PGFPlots 生成 LaTeX 原生可视化
- 使用脚本提前生成图片，然后以插图形式引入

对于脚本生成的插图，当 `matplotlib` 和 `seaborn` 等 Python 工具是制作准确教学图片的最清晰方式时，请优先使用它们。

当可视化是外部生成而非在 LaTeX 中原生绘制时：

- 将图片导出为 `pdf`，以便插入 `.tex` 时避免栅格化损失
- 对于绘图、图表和示意性插图，优先使用矢量输出
- 除非内容本质上是栅格的，否则避免对脚本生成的教学图片使用 `png` 或 `jpg`

当源材料中的关系、结果或公式在重绘后比直接截图更清晰时，应优先重绘，而不是勉强保留信息密度过高的截图。

### 设计流程类 TikZ 图

当源内容讲解设计流程、系统架构、模块协作、决策链、失败回退或阶段演进时，必须优先考虑使用 TikZ / PGFPlots 重绘为 LaTeX 原生图，而不是只用文字顺序复述。

适合使用 TikZ 的典型内容包括：

- 从需求、约束、方案到实现的设计流程
- 架构分层、模块边界、组件协作和数据流 / 控制流
- 训练、部署、评估、上线、回滚等工程管道
- 多阶段递进、迭代反馈、失败回退和决策分支
- 源截图包含高价值流程关系，但原图拥挤、低清或不便阅读

以下情况不要强行画图：

- 只是普通要点枚举，节点之间没有明确关系
- 源内容没有给出稳定结构，图形只能靠猜测补全
- 截图或幻灯片已经足够清晰，重绘只会重复信息
- 图形只起装饰作用，不能降低理解成本

每张 TikZ 图都应遵循固定讲解顺序：图前先用正文说明它要解决的理解问题；图中只放短标签和必要连接；图后解释读图方式、关键路径和读者应带走的结论。
流程图、架构图、机制图和阶段演进图不得把原始 `tikzpicture` 直接写进最终主 `.tex` 文档；应先作为独立图稿编译为 PDF，再在最终文档的普通 `figure` 环境中用 `\includegraphics` 插入。
插入后的图不要放入 `importantbox`、`knowledgebox` 或 `warningbox`。
若 TikZ 图是基于视频片段抽象重绘的，应在 caption 或附近脚注标注来源时间区间；若综合多段内容，应写明综合自哪些时间区间。

默认使用 `assets/tikz-styles.tex` 中的工程白板式 TikZ 样式；创建独立图稿时可从 `assets/tikz-figure-template.tex` 复制起步。`flowstep` 表示流程阶段，`decision` 表示判断或取舍，`artifact` 表示输入、输出、文档、模型或数据，`risknode` 表示风险、失败或回退条件，`flowarrow` 表示主流程箭头，`feedbackarrow` 表示反馈、迭代或回退路径，`layerbox` 表示模块层、阶段组或系统边界。
图形应保持低饱和、细边框、无阴影、无渐变；每张图建议控制在 4--8 个主要节点，超过时拆成总览图和局部图。

### 独立 TikZ 图稿流程

对每一张流程图、架构图、机制图或阶段演进图，应在任务目录下创建独立源码与产物目录，例如：

```text
$TASK_DIR/figures/tikz-src/csa-hca-flow.tex
$TASK_DIR/figures/tikz-pdf/csa-hca-flow.pdf
```

独立图稿应使用 `standalone` 类编译。创建图稿目录时，把技能目录中的 `assets/tikz-styles.tex` 复制到 `figures/tikz-src/`，让每张图稿在自己的源码目录中解析统一样式，避免最终笔记目录结构影响图稿编译。编译命令示例：

```bash
SKILL_DIR="$(cd "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/.." && pwd)"
mkdir -p "$TASK_DIR/figures/tikz-src" "$TASK_DIR/figures/tikz-pdf"
cp "$SKILL_DIR/assets/tikz-styles.tex" "$TASK_DIR/figures/tikz-src/tikz-styles.tex"
cd "$TASK_DIR/figures/tikz-src"
latexmk -xelatex -interaction=nonstopmode -halt-on-error \
  -outdir="$TASK_DIR/figures/tikz-pdf" \
  csa-hca-flow.tex
```

图稿 PDF 通过视觉复核后，再在最终主 `.tex` 中插入该 PDF：

```tex
\begin{figure}[H]
\centering
\includegraphics[width=0.92\textwidth]{figures/tikz-pdf/csa-hca-flow.pdf}
\caption{CSA 与 HCA 的压缩注意力流程\protect\footnotemark}
\end{figure}
\footnotetext{抽象自视频 03:41--07:14 对 CSA、HCA 结构差异的讲解。}
```

主文档不再承担流程图布局求解职责，只负责把已验证的图稿 PDF 与正文、caption 和脚注组合排版。若最终页面中图稿过大、过小或与 caption / 脚注分页不稳定，应优先调整 `\includegraphics` 宽度、图稿边距或正文位置；若图稿内部有问题，则回到独立 TikZ 源码修复并重新编译。

### TikZ 图稿 PDF 视觉复核

只要生成 TikZ 或 PGFPlots 图稿，独立图稿 PDF 编译成功之后必须先对该图稿做视觉复核；最终主 PDF 编译成功之后，还必须复核图稿所在页面的组合效果。不能只依赖 LaTeX 编译日志或源码检查来判断图形可交付。复核时优先直接查看 PDF 页面；如果当前环境不便直接查看 PDF，则将图稿 PDF 或最终主 PDF 的相关页面渲染为 PNG 后检查，例如使用 `pdftoppm -png -r 150 figure.pdf figure-page` 或 `pdftoppm -png -r 150 -f <page> -l <page> output.pdf tikz-page`。

复核重点包括：节点、标签、箭头、分组框、caption 和脚注是否互相重叠；节点文字是否溢出或小到不可读；箭头是否错误穿过关键文字或造成方向歧义；`layerbox` 是否遮挡主节点；图是否超出页边距或被缩放到失去阅读价值；颜色、线宽和节点样式是否仍符合工程白板式的低饱和、细边框、无阴影、无渐变要求。

发现图稿内部问题时应修改独立 TikZ 源码并重新编译，而不是对渲染后的位图做补丁，也不是在最终主文档里临时覆盖样式。常用修复手段包括调整 `node distance`、改用 `above/below left/right`、缩短节点标签、增加换行、拆分过密图、用 `bend left/right` 或 `out/in` 调整箭头路径、移动 `layerbox` 范围、控制 standalone 图稿边距，以及把超过 8 个主要节点的图拆成总览图和局部图。若复核后仍存在明显重叠、文字溢出、不可读或风格失控的问题，该 PDF 不应交付。

可视化适用于以下场景：

- 流程、管道和架构概览
- 曲线和图表，如缩放定律、训练曲线、基准测试结果和消融对比
- 分布、相关性、热图和其他解释数据关系的图表
- 复杂函数、曲面、等高线图和几何直观图
- 重绘为图表后更清晰的表格或对比
- 将某节的核心机制或要点压缩为一张图的总结示意图

不要添加没有任何教学意义的装饰性图形。

## Coverage Review

正式交付前默认执行独立漏召回审查，并将结果落盘为：

```text
$TASK_DIR/output/coverage_review.md
```

审查输入应包括：原始字幕或 ASR `raw.srt`、清洗轨 `clean.srt`（若存在）、章节计划或最终目录、关键帧清单、最终 `.tex`。审查输出只反馈问题，不直接修改正文。

重点检查：

- 是否遗漏重要概念、关键例子、公式、代码、实验结论、讲者强调或有信息量的对话片段
- 是否把源视频的具体细节过度概括，导致可验证信息丢失
- 是否存在图文不匹配、时间脚注和实际帧不一致、对话摘录缺少语境的问题
- 是否有重要视觉材料只在 OCR 或字幕中被提及，但没有被看图确认或纳入正文
- 是否有章节衔接断裂、术语前后不一致、同一概念重复定义的问题

长视频、课程视频、多 P 视频、访谈/圆桌/播客视频默认必须执行 coverage review。若用户明确要求快速草稿，可以跳过；最终回复中必须说明未做漏召回审查。

如果环境支持且用户明确允许子代理，可用独立 reviewer agent 执行该阶段；否则由主代理切换到独立审查视角完成。

## 最终检查清单

在交付前，请核实以下所有内容：

- 没有遗漏重要的教学内容，且在浓缩、重构或总结过程中没有丢失具体但关键的细节
- 若存在文本轨，已保留 `subtitles/raw.srt`；若生成 `subtitles/clean.srt`，已运行 `check_clean_srt.py` 并复核告警
- 若正式交付未被用户要求快速跳过，已生成 `output/coverage_review.md` 并处理其中确认为有效的问题
- 文本与图片保持一致：每张插入的视觉素材都支撑周围的解释；若该素材来自视频帧，应确认裁剪和选帧都已足够准确
- 文档在教学意义上足够视觉丰富：检查是否应添加更多高信息量的关键帧、配图、重绘图表或 LaTeX / Python 生成插图，以提升清晰度
- 若文档包含 TikZ 或 PGFPlots 图稿，必须确认每张图都已先独立编译为 PDF 并完成图稿级视觉复核；最终主 PDF 编译后还要查看相关页面或渲染页图，确认图稿插入后没有裁切、过度缩放、caption / 脚注错位、重叠、遮挡、溢出、不可读、箭头歧义和样式失控问题
- 默认使用 `xelatex` 或 `latexmk -xelatex` 这类 Unicode 中文引擎编译，不要把 `pdflatex` 当作默认编译路径
- 最终输出文件名应根据源内容实际主题命名为 5-10 个字符，避免使用泛化标题、平台原始长标题或无语义短名

## 交付

请交付以下内容：

- 最终的 `.tex` 文件
- 编译后的 PDF
- 文档引用的任何提取或生成的图片素材
- 独立 TikZ / PGFPlots 图稿的 `.tex` 源文件和已编译 PDF
- 在可用且有价值时，首页引用的封面图或头图
- 在使用字幕或本地语音转文字时，交付 `subtitles/raw.srt`；若生成清洗轨，一并交付 `subtitles/clean.srt`
- 在使用本地语音转文字时，交付转录输出（`.srt` 和 `.json`）
- 正式交付时优先包含 `output/coverage_review.md`；若跳过，说明原因
- 在采用视频内容包工作流时，优先同时交付 `metadata/source.json`

交付物命名规则：

- PDF、`.tex` 以及主输出目录都应根据源内容实际主题命名
- 名称长度以 5-10 个中文字符为宜
- 名称应概括核心主题，而不是简单照抄平台原始长标题
- 不要使用 `note`、`output`、`final`、`课程笔记1` 这类弱语义名称

在回复最终产物路径时：

- 始终包含生成输出的本地文件系统路径
- 优先提供位于 `VIDEO2NOTE_TMPDIR` 下对应任务目录中的 PDF 和 `.tex` 路径
- 若转录结果、图片目录或中间素材属于交付物，则一并包含
- 如果在 WSL 中运行，还请提供可直接在 Windows 文件资源管理器中打开的路径，使用 `wslpath -w` 转换
- 使用 `wslpath -w <linux_path>` 推导 Windows 路径，而不是手写
- 例如，将 `/tmp/video2note/task-001/output.pdf` 转换为 `\\wsl.localhost\Ubuntu-22.04\tmp\video2note\task-001\output.pdf`

## 素材

- `assets/notes-template.tex`：默认的 LaTeX 填充模板
- `assets/tikz-styles.tex`：独立 TikZ / PGFPlots 图稿与模板共用的工程白板式样式
- `assets/tikz-figure-template.tex`：独立 TikZ 图稿起始模板
- `runtime/check_clean_srt.py`：清洗字幕轨与原始字幕轨的结构校验脚本
