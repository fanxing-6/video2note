# 30 Analysis Outline

在写任何正文前读取本卡片。目标是先建立可检查的分析骨架，禁止直接压缩 transcript。

## 输入

- `metadata/source.json`
- `subtitles/raw.srt`
- 可选 `subtitles/clean.srt`
- 视觉素材清单
- `assets/report-blueprints.md`
- `assets/depth-ladders.md`
- `assets/analysis-outline-template.md`

## 输出

- `analysis/outline.md`
- 可选：`analysis/units.json`

## 蓝图选择

- 对谈、圆桌、播客、Q&A：Conversation / Roundtable / Podcast。
- 论文讲解、课程讲授、方法拆解：Lecture / Tutorial / Paper Explanation。
- 系统设计、产品架构、工程复盘：System / Product Architecture。
- 职业路径、行业下注、岗位选择：可叠加 Market / Career / Decision Analysis。

未显式选择蓝图即进入正文，视为流程未通过。

## 主题单元

每个主题单元至少包含：

- `question`
- `core_claim`
- `mechanism`
- `evidence_with_timestamps`
- `formula_or_metric`
- `cost_or_constraint_model`
- `architecture_or_decision_flow`
- `actionable_takeaways`

35--60 分钟高密度对谈、圆桌、播客或 Q&A 默认 8--12 个主题单元。公式/训练/论文讲解和工程/架构视频默认至少 6 个主题单元，除非材料明显短或低密度。

## 深度规则

- 每个主题单元映射至少一个 depth ladder。
- 支持的内容必须下钻到公式/指标、成本/约束、架构/流程或行动建议。
- 不支持的字段写 `N/A`，并写具体原因。
- `N/A` 不能用于回避该做的建模或图示。

## 门禁

- `analysis/outline.md` 存在。
- outline 顶部记录 `selected_blueprint`, `secondary_blueprint`, `active_depth_ladders`, `target_reader`。
- 每个主题单元字段完整。
- stage ledger 记录 outline 路径、主题单元数量、N/A 数量和下一阶段输入。
