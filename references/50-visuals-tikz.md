# 50 Visuals/Web-SVG/TikZ

在选择截图、裁剪、重绘图、生成 Web/SVG 信息图或少量 TikZ/PGFPlots 前读取本卡片。目标是让视觉素材服务讲解，而不是装饰；同时避免图内文字、箭头、节点、表格、图例和说明框出现不合理重叠。

## 输入

- `analysis/outline.md`
- 本地视频、contact sheet、候选帧
- 可复用的 `figure-theme` 约定：字体、色板、线宽、圆角、标题层级、callout 样式、画布尺寸
- 可选：Web/SVG/D3/ELK/Vega-Lite 绘图脚本或现成图稿源文件
- 可选：`assets/tikz-figure-template.tex`
- 可选：`assets/tikz-styles.tex`

## 输出

- 可选截图或裁剪图
- `figures/src/*`：可编辑图稿源文件，例如 `.svg`, `.html`, `.js`, `.json`, `.mmd`, `.tex`
- `figures/svg/*.svg`：规范化后的矢量源图，若使用 Web/SVG 路线
- `figures/pdf/*.pdf`：LaTeX 默认插入的最终矢量图稿
- `figures/preview/*.png`：用于人眼抽检和最终 review 的预览图
- 可选：`figures/tikz-src/*.tex` 与 `figures/tikz-pdf/*.pdf`
- 图稿视觉抽检记录

## 选帧规则

- 先高召回检查候选帧，再选择最清晰、最完整、最相关的一帧。
- 文字、公式、标签、表格、代码必须可读。
- 幻灯片或白板逐步构建时，优先最终完整状态。
- 不要只因同一时间附近有相关字幕就插入截图；必须亲自查看图像。
- 低清、重复、装饰性或不能支撑正文的帧应舍弃。

## 默认绘图路线

所有非截图类重绘图先进入统一 `figure-theme`，再选择实现工具。实现工具可以不同，但最终图面必须像同一套图形系统：同一字体、色板、线宽、圆角、箭头、标题层级、说明框、留白和 caption 语气。

- 流程图、pipeline、DAG、模块依赖、专家合并链路：优先使用 ELK.js 计算布局，再用 D3/SVG 或原生 SVG 组件套统一主题渲染。ELK 负责避免节点重叠和边线穿插，D3/SVG 负责视觉风格。
- 指标图、实验对比图、柱状图、散点图、分面图：优先使用 Vega-Lite 生成图表内核，再包进统一 SVG 外壳。必须显式固定 color domain，避免同一模型或方法在不同图里颜色语义漂移。
- 机制图、概念图、token-level 分布图、公式旁注图：优先使用 D3/SVG 或原生 SVG 组件。节点、箭头、标注和 callout 必须有明确布局区域，不要靠手写坐标硬塞。
- 草图感、白板感、课堂推演感：可选 Rough.js / Excalidraw-like 风格，但默认不作为正式研究讲义主图风格，除非用户明确要求。
- Mermaid 适合快速草稿和低风险文档流程图，但不是默认最终出图方案；若使用 Mermaid，仍必须经过统一主题、SVG/PDF 导出和视觉验收。

## LaTeX 插图格式

- Web/SVG 负责生产和编辑，SVG 保留为可编辑源图。
- PDF 是默认插入主 `.tex` 的最终格式：`\includegraphics[width=\textwidth]{figures/pdf/name.pdf}`。
- PNG 只用于预览、截图类素材、复杂 CSS/foreignObject 转 PDF 不一致时的兜底，且必须高分辨率导出。
- 不要让主 LaTeX 文档依赖直接插入 SVG；这通常会引入 shell-escape、Inkscape、字体替换和环境差异。
- 若图稿需要跨机器交付，优先确认 PDF 字体已嵌入；必要时将图中文字转 path，但要在 review 中记录可搜索性损失。

## TikZ/PGFPlots 规则

- TikZ 只作为受限补充，适合简单数学几何图、少节点推导图、PGFPlots 原生数值图，不再作为复杂信息图的默认方案。
- 流程图、架构图、机制图和阶段演进图若用 TikZ，必须独立编译成 PDF，再用 `\includegraphics` 插入主文档。
- 主 `.tex` 不直接承载复杂 TikZ 布局。
- 每张 TikZ 图建议 4--6 个主要节点；过密、长中文、多图例、多 callout 或表格混排时，改用 Web/SVG 路线。
- TikZ 图也必须服从统一 `figure-theme`，不能出现与 Web/SVG 图稿割裂的字体、颜色、线宽或圆角风格。

## 信息密度规则

- 一张图只承担一个主要教学判断。不要把表格、四组柱状图、pipeline、三角坐标和长说明框堆进同一张图。
- 当图内文字超过约 80--120 个中文字，优先拆成“图 + 正文解释”或“图 + 表格”，而不是继续压缩字号。
- 图例、注释和 callout 要有固定区域；不得覆盖数据区、箭头、节点或轴标签。
- 中文标签优先短语化；长解释写到 caption、正文或单独 callout。

## 视觉复核

独立图稿导出后必须复核。默认链路是：源图 -> SVG -> PDF -> PNG 预览 -> 主 PDF 抽检。

- 节点和标签是否重叠
- 箭头是否穿过文字或方向歧义
- 节点文字是否溢出
- 图是否太小、超页边距、被裁切或被错误缩放
- 最小字号是否仍可读；正式报告图内文字通常不低于 12px 等效大小
- 自动布局结果是否按 bounding box 缩放进画布
- Vega-Lite / 图表库是否显式固定颜色 domain、排序和轴范围
- SVG/PDF/PNG 三者是否视觉一致
- caption、脚注与图是否在最终 PDF 中组合稳定

## 门禁

- 每张插图都有明确教学用途。
- 视频帧或裁剪图附近记录来源时间区间。
- Web/SVG 图稿保留源文件、SVG、PDF 和 PNG 预览；TikZ/PGFPlots 图稿保留 `.tex` 和 PDF。
- 主 `.tex` 默认插入 `figures/pdf/*.pdf`，PNG 兜底必须说明原因。
- stage ledger 记录工具选择、figure-theme、图稿路径、导出格式、视觉抽检结果和修复项。
