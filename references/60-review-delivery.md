# 60 Review/Delivery

在 PDF 编译后、最终交付前读取本卡片。目标是独立检查内容覆盖、分析深度、落地性和排版可交付性。

## 输入

- `metadata/source.json`
- `analysis/stage-ledger.md`
- `analysis/outline.md`
- `subtitles/raw.srt`
- 主 `.tex`
- 主 PDF
- 视觉素材和图稿
- `assets/coverage-review-template.md`

## 输出

- `output/coverage_review.md`
- 最终 PDF 和 `.tex`
- 最终回复中的交付路径与风险说明

## Review 护栏

- 文风：元叙述是否高频出现；是否连续长段落；是否把 `dialoguebox` 当正文主线。
- 结构：蓝图是否合理；主题单元是否足够；是否遗漏明显支线；章节是否过粗。
- 深度：概念、机制、证据是否齐；支持的章节是否有公式/指标、成本/约束、架构/流程。
- 落地：是否给出判断框架、使用建议、选择建议或避坑提醒。
- 图文：截图、图稿、caption、脚注、时间区间是否匹配。
- `N/A`：是否确实不适用，还是写作阶段漏做。
- 阶段遵循：`stage-ledger.md` 是否证明每阶段重新读取了对应卡片。

## 自动检查建议

- grep 元叙述词：`讲者|访谈|这场讨论|这期视频|视频中提到|这一段讨论`。
- 统计超过 4 句的正文段落。
- 检查 `analysis/outline.md` 是否包含主题单元字段。
- 检查 PDF 页数、编译日志和图稿 PDF 是否存在。
- 渲染关键 PDF 页面为 PNG 后做视觉抽检。

## 交付规则

最终回复包含：

- PDF 路径
- `.tex` 路径
- `analysis/outline.md`
- `analysis/stage-ledger.md`
- `output/coverage_review.md`
- 图稿或素材目录
- 未完成、降级或残余风险

## 门禁

- `coverage_review.md` 存在。
- PDF 编译成功。
- 关键页面视觉抽检通过。
- Review 发现的有效问题已修复，或在最终回复中说明未修复原因。
