# 10 Acquire

在获取或复用视频素材前读取本卡片。目标是把平台差异收敛成统一内容包。

## 输入

- 视频 URL 或已有 `$TASK_DIR/metadata/source.json`
- `$TASK_DIR`
- 平台 SOP

## 输出

- `metadata/info.json`
- `metadata/formats.txt`
- `metadata/subtitles.txt`
- `cover/cover.*`
- `source/video.*`
- `metadata/source.json`
- 可选：`frames/contact_sheet.png`

## 平台路由

- Bilibili URL 或 `b23.tv`：读取 `sops/bilibili.md`。
- YouTube URL：读取 `sops/youtube.md`。
- TikTok / Douyin：读取 `sops/tiktok-douyin.md`。
- 已有本地内容包：验证 `metadata/source.json` 和引用文件存在，不重新下载。

## 硬规则

- 本阶段不实现“搜索视频”。搜索只可作为人工取样方式，不能固化为 skill 能力。
- 先探测元数据、格式、字幕和分 P，再下载主视频。
- 多 P 视频必须先明确处理范围；未确认前不要全量下载。
- 优先下载官方封面或高价值头图。
- 目标不是理论最高分辨率，而是当前环境能稳定下载、适合抽帧和 OCR 的最佳版本。
- 如果需要 Cookie 才能获取 1080P+，可尝试 Cookie；失败后允许降级到公开可下载版本并记录。

## 统一内容包

整理到：

```text
$TASK_DIR/metadata/source.json
```

至少记录：

- 标题、作者、发布日期、时长、来源 URL
- 封面路径
- 本地视频路径
- 字幕/ASR/OCR/视觉素材路径
- `analysis_outline_path`
- `coverage_review_path`
- `locator_type: time_range`

## 门禁

- 有 `source.json`。
- 至少具备以下之一：封面 + 字幕 + 本地视频；封面 + ASR 输入视频；封面 + 视频 + 视觉分析素材。
- stage ledger 已记录采集来源、是否复用素材、是否有降级。
