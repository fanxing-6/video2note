# 40 Writing LaTeX

在生成主 `.tex` 前读取本卡片。目标是把分析骨架写成专家讲义型主题报告，而不是视频复盘。

## 输入

- `analysis/outline.md`
- `metadata/source.json`
- `assets/notes-template.tex`
- 必要 transcript 片段和视觉素材
- 已编译或待编译图稿路径

## 输出

- 主 `.tex`
- 主 PDF 初版

## 正文硬规则

- 正文直接讲主题判断、机制、约束和推导，不写“这期视频讲了什么”的复盘。
- 除封面元数据、脚注或 `dialoguebox` 外，避免“讲者认为”“访谈里”“这场讨论”“这期视频”“视频中提到”“这一段讨论”等元叙述。
- 每段只承载一个主判断，通常 2--4 句；超过 4 句必须检查是否拆段。
- 章节开头先给判断，再解释概念、机制、形式化层、证据和行动建议。
- 证据时间戳放脚注、caption、review 或少量高信号证据块，不作为正文主叙事。

## 公式、代码和行动建议

- 出现公式时，先解释公式要表达什么，再展示公式，再解释变量。
- 公式使用 LaTeX 数学环境，不放进 Markdown 代码块。
- 代码示例使用 `lstlisting`，只保留支撑机制的核心片段。
- 每个重要章节都落到“如何判断 / 如何选择 / 如何使用 / 如何避坑”之一。

## Box 使用

- `importantbox` 承载核心结论、机制摘要或关键步骤。
- `knowledgebox` 承载背景、术语对比、工程上下文和直觉类比。
- `warningbox` 承载误解、隐藏前提、易错实现点和风险。
- `dialoguebox` 只用于对谈类材料的短原话证据，不作为正文骨架。

## 门禁

- 主 `.tex` 从 `\documentclass` 到 `\end{document}` 完整。
- 使用 `xelatex` 或 `latexmk -xelatex` 编译。
- 正文与 `analysis/outline.md` 的主题单元对应。
- stage ledger 记录 `.tex`、PDF 初版、编译状态和待 review 问题。
