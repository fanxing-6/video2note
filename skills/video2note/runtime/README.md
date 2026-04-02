# Runtime

`video2note` 的本地运行时辅助脚本。

默认技术栈：

- **ASR**：`faster-whisper`，模型 `whisper-large-v3`
- **OCR**：`PaddleOCR`，模型 `PP-OCRv5_server`

模型执行策略：

- 任何依赖模型的步骤都应默认优先使用 GPU。
- Whisper 转录在存在可用 GPU 时应在 `--device cuda` 上运行。
- “较大的 GPU 批大小优先”表示探索顺序，而不是固定默认值；不同显存、模型和音频长度下稳定值不同。
- 共享运行时只有在 CUDA 依赖完整时，GPU 主路径才算可用。若缺少 `libcublas`、`libcudnn` 或 `nvrtc` 相关库，应先补齐运行时依赖。
- 对 `large-v3` 的真实长音频，默认从更保守的 GPU `batch-size` 起步，再逐步上探；仅在 GPU 不可用或明确出现故障时，才回退到 CPU。

## 目录职责

- `skills/video2note/runtime/`：仅表示运行时脚本源码目录
- `VIDEO2NOTE_HOME`：唯一真实共享运行时目录
- `VIDEO2NOTE_TMPDIR`：任务产出根目录

默认目录约定：

- 共享运行时根目录：`$HOME/video2note`；若当前 shell 未设置 `HOME`，则回退到 `$USERPROFILE/video2note`
- 共享虚拟环境：`$VIDEO2NOTE_HOME/.venv`
- 任务产出根目录：`${TMPDIR:-/tmp}/video2note`；若 `TMPDIR` 不存在，则回退到 `${TEMP}`、`${TMP}` 或 `/tmp/video2note`

## 初始化方式

运行时脚本源码目录中提供：

- `setup_runtime.sh`
- `env.sh`

这两个脚本应通过其**实际源码路径**调用，但其效果始终作用于用户级运行时目录，而不是脚本源码目录本身。

例如：

```bash
bash <runtime-scripts-dir>/setup_runtime.sh
source <runtime-scripts-dir>/env.sh
```

上述命令将：

- 创建 `VIDEO2NOTE_HOME`
- 在 `VIDEO2NOTE_HOME/.venv` 中创建一个隔离的 Python 3.10 虚拟环境
- 创建 `VIDEO2NOTE_TMPDIR`
- 导出 `VIDEO2NOTE_HOME`、`VIDEO2NOTE_VENV`、`VIDEO2NOTE_TMPDIR` 和 `VIDEO2NOTE_RUNTIME_SCRIPTS_DIR`

安装的包包括：

- `faster-whisper`
- `paddleocr`
- `paddlepaddle==3.2.0`

安装前可选的环境变量：

- `VIDEO2NOTE_HOME=/path/to/video2note-home`
- `VIDEO2NOTE_VENV=/path/to/video2note-home/.venv`
- `VIDEO2NOTE_TMPDIR=/path/to/temp/video2note`
- `PADDLE_MODE=cpu|gpu-cu118|gpu-cu126`
- `ASR_CUDA=off|pip-cu12`
- `PYTHON_BIN=/usr/bin/python3.10`

当 `ASR_CUDA=pip-cu12` 时，`setup_runtime.sh` 会为共享 venv 安装：

- `nvidia-cublas-cu12`
- `nvidia-cudnn-cu12==9.*`
- `nvidia-cuda-nvrtc-cu12`

辅助脚本：

- `transcribe_with_faster_whisper.py`
- `run_ppocrv5.py`
- `merge_chunked_transcripts.py`
- `resolve_dlpanda.py`

使用示例：

```bash
source <runtime-scripts-dir>/env.sh
TASK_DIR="$VIDEO2NOTE_TMPDIR/task-001"
mkdir -p "$TASK_DIR"
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/transcribe_with_faster_whisper.py" input.wav --model large-v3 --language zh --device cuda --batch-size 8 --output-dir "$TASK_DIR/transcript"
python "$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR/run_ppocrv5.py" frames/ --device cpu --output-dir "$TASK_DIR/ocr-out"
```

### GPU ASR 前置检查

在把 GPU 作为主路径前，至少应确认：

- 已 `source <runtime-scripts-dir>/env.sh`
- 共享 venv 已安装 CUDA 运行时轮子
- `transcribe_with_faster_whisper.py` 能成功加载 CUDA 模型

若出现以下错误，应优先按对应类别处理：

- `libcublas` / `libcudnn` / `nvrtc` 缺失：先补运行时依赖
- `CUDA out of memory`：优先降低 `batch-size`，继续坚持 GPU

建议每次任务都在 `VIDEO2NOTE_TMPDIR` 下创建独立子目录，避免不同任务之间互相覆盖。
