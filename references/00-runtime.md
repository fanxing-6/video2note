# 00 Runtime

在任何采集、转录、写作或 review 前读取本卡片。目标是准备稳定运行环境、任务目录和阶段账本。

## 输入

- 用户给出的视频 URL、本地内容包，或已经存在的 `$TASK_DIR`
- skill 根目录
- 当前 shell 环境

## 输出

- 已初始化的 `$TASK_DIR`
- `$TASK_DIR/analysis/stage-ledger.md`
- 可用的 `VIDEO2NOTE_HOME`
- 可用的 `VIDEO2NOTE_RUNTIME_SCRIPTS_DIR`
- 可用的 Python/Whisper/OCR/LaTeX 基础工具状态

## 运行时基线

- ASR 默认使用 `faster-whisper`，模型 `large-v3`。
- OCR 默认使用 PaddleOCR PP-OCRv5 server。
- 共享运行时根目录是 `$VIDEO2NOTE_HOME`，默认 `$HOME/video2note`。
- 共享虚拟环境是 `$VIDEO2NOTE_HOME/.venv`。
- 任务目录默认位于 `$VIDEO2NOTE_TMPDIR` 下，每个任务必须独立子目录。
- `runtime/` 是脚本源码目录，不是真实运行时目录。

## 硬规则

- 先尝试 `source runtime/env.sh`；若 venv 不存在，运行 `runtime/setup_runtime.sh`。
- 模型步骤默认优先 GPU。Whisper 优先 `--device cuda`，OOM 时先降 batch size，不要直接回退 CPU。
- 自动化脚本中调用 `ffmpeg` 必须带 `-nostdin`，防止读取后续脚本内容。
- 不要把下载、抽音频、ASR 并行触发；上一产物稳定落盘后再进入下一步。
- 不要在 skill 仓库里写任务输出；任务输出写到 `$TASK_DIR`。

## Stage Ledger

创建或更新：

```text
$TASK_DIR/analysis/stage-ledger.md
```

每个阶段追加：

```markdown
## Stage XX: name

- card_read: references/XX-name.md
- started_at:
- inputs:
- outputs:
- gate_result: pass | blocked | degraded
- unresolved:
- next_stage:
```

若阶段失败，先把失败原因写入 ledger，再决定重试、降级或停止。

## 门禁

- `$TASK_DIR` 已创建，且包含 `metadata/`, `analysis/`, `output/`。
- `stage-ledger.md` 已记录本阶段。
- 运行时脚本路径明确。
- 若 GPU 不可用，ledger 中记录原因和回退路径。
