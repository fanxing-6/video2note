---
name: video2note
description: 根据用户提供的 Bilibili、YouTube、TikTok 或 Douyin 等视频内容，生成一份专家讲义型、结构化的中文 LaTeX 深度报告及最终 PDF。
---
# Video2Note

将视频内容转换为一份可复查、可编译、可交付的中文专家讲义型深度报告。默认交付完整 `.tex`、PDF、分析骨架、素材、图稿和 coverage review。

本文件只承担入口路由和全局契约。执行细节必须按阶段重新读取 `references/` 中对应卡片，不允许只读本文件后凭记忆跑完整流程。

## 不可跳过的执行原则

- 每进入一个阶段，先读取该阶段卡片，并在 `$TASK_DIR/analysis/stage-ledger.md` 记录已读卡片、输入、输出、门禁结果和下一阶段。
- 最终报告不得直接从 transcript 压缩生成；必须先形成 `analysis/outline.md`。
- 正文写主题报告，不写视频复盘；除封面元数据、脚注或 `dialoguebox` 外，正文尽量不出现“讲者/访谈/这期视频/视频中提到/这一段讨论”等元叙述。
- 当材料支持时，必须覆盖“概念 -> 机制 -> 公式/指标/成本约束 -> 架构/流程 -> 行动建议”；不支持时在分析骨架里标记 `N/A` 并写原因。
- 图片、Web/SVG/PDF 图稿、必要的 TikZ、公式、代码、时间戳和 review 都是交付质量的一部分，不是可选装饰。
- 搜索视频不是本 skill 的产品能力；skill 处理的是已经确定的视频源或本地内容包。

## 阶段索引

按顺序执行。除非用户明确要求快速草稿，否则不要跳过阶段。

| 阶段 | 何时读取 | 卡片 |
| --- | --- | --- |
| 00 Runtime | 任务开始、切换环境、初始化目录 | `references/00-runtime.md` |
| 10 Acquire | 已有 URL 或本地内容包，准备采集素材 | `references/10-acquire.md` |
| 20 Transcribe/OCR | 需要字幕、ASR、OCR、关键帧或视觉素材 | `references/20-transcribe-ocr.md` |
| 30 Analysis | 写正文之前 | `references/30-analysis-outline.md` |
| 40 Writing | 生成 LaTeX 正文之前 | `references/40-writing-latex.md` |
| 50 Visuals/Web-SVG/TikZ | 需要流程图、架构图、机制图、截图或重绘图 | `references/50-visuals-tikz.md` |
| 60 Review/Deliver | 编译 PDF 后、最终回复前 | `references/60-review-delivery.md` |

平台采集细节仍由 SOP 承担：

- Bilibili：`sops/bilibili.md`
- YouTube：`sops/youtube.md`
- TikTok / Douyin：`sops/tiktok-douyin.md`

## 统一内容包

进入分析和写作前，任务目录中应存在：

```text
$TASK_DIR/metadata/source.json
```

推荐字段：

- `source_kind`: `video`
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
- `analysis_outline_path`
- `coverage_review_path`
- `visual_artifacts[]`
- `locator_type`: `time_range`

写作层只消费统一内容包、分析骨架、必要文本轨和视觉素材；不要回头耦合某个平台的原始采集命令。

## 必交中间产物

每个正式任务默认保留以下产物：

- `metadata/source.json`
- `analysis/stage-ledger.md`
- `analysis/outline.md`
- `subtitles/raw.srt`，若使用字幕或 ASR
- `subtitles/clean.srt`，若生成清洗轨
- `subtitles/transcript.json`，若使用本地 ASR
- `figures/src/*`, `figures/svg/*.svg`, `figures/pdf/*.pdf`, `figures/preview/*.png`，若生成 Web/SVG 图稿
- `figures/tikz-src/*.tex` 与 `figures/tikz-pdf/*.pdf`，若生成 TikZ/PGFPlots 图稿
- 主 `.tex`
- 主 PDF
- `output/coverage_review.md`

## 目标报告契约

报告的默认站位是“专家讲义”，不是“视频复盘”。

- 结构要中细粒度；35--60 分钟高密度对谈、圆桌、播客或 Q&A 默认拆成 8--12 个主题单元。
- 公式/训练/论文讲解类材料必须解释概念、机制、公式、变量、实现或评估方式，并给行动建议。
- 工程/系统/架构类材料必须显式建模模块边界、数据流/控制流、成本/延迟/吞吐/显存/资源约束和部署判断。
- 对谈/职业/行业判断类材料必须抽象决策框架、约束模型、下注逻辑或读者行动路径。
- 每个主要章节应以“如何判断 / 如何选择 / 如何使用 / 如何避坑”中的至少一种动作收束。

## 写作与排版入口

- 主文档从 `assets/notes-template.tex` 起步，不要重复定义模板已有基础样式。
- 蓝图从 `assets/report-blueprints.md` 选择，并记录在 `analysis/outline.md`。
- 深度梯子从 `assets/depth-ladders.md` 选择，并记录在 `analysis/outline.md`。
- 分析骨架可从 `assets/analysis-outline-template.md` 起步。
- Coverage review 可从 `assets/coverage-review-template.md` 起步。
- 图稿默认采用统一 `figure-theme` 后由 Web/SVG/D3/ELK/Vega-Lite 生成，主 LaTeX 默认插入最终 PDF 图稿。
- TikZ 仅用于简单数学几何图、少节点推导图或 PGFPlots 数值图；可从 `assets/tikz-figure-template.tex` 起步，并复用 `assets/tikz-styles.tex`。

## 最终验收门禁

交付前逐项确认：

- `analysis/stage-ledger.md` 显示每个阶段都重新读取了对应阶段卡片。
- `analysis/outline.md` 存在，包含所选蓝图、深度梯子和主题单元字段。
- 正文几乎不含元叙述，段落通常 2--4 句，未连续堆叠长摘要段。
- 支持的章节没有缺失公式/指标、成本/约束、架构/流程或行动建议。
- 每个 `N/A` 都有理由，并在 review 中复核合理性。
- PDF 使用 XeLaTeX 或 `latexmk -xelatex` 编译成功。
- 插图和图稿经过 SVG/PDF/PNG 视觉抽检；图文、caption、脚注和来源时间区间一致。
- `output/coverage_review.md` 存在并记录结构、深度、落地性和残余风险。

## 交付回复

最终回复只给高信号结果：

- PDF 路径
- `.tex` 路径
- `analysis/outline.md`
- `analysis/stage-ledger.md`
- `output/coverage_review.md`
- 关键素材目录或图稿目录
- 未完成项、降级项或残余风险
