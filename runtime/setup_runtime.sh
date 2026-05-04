#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_HOME="${HOME:-${USERPROFILE:-}}"
if [[ -z "$USER_HOME" ]]; then
  echo "Neither HOME nor USERPROFILE is set" >&2
  exit 1
fi
VIDEO2NOTE_HOME="${VIDEO2NOTE_HOME:-$USER_HOME/video2note}"
VIDEO2NOTE_VENV="${VIDEO2NOTE_VENV:-$VIDEO2NOTE_HOME/.venv}"
TMP_BASE="${TMPDIR:-${TEMP:-${TMP:-/tmp}}}"
VIDEO2NOTE_TMPDIR="${VIDEO2NOTE_TMPDIR:-$TMP_BASE/video2note}"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3.10}"
PADDLE_MODE="${PADDLE_MODE:-cpu}"
ASR_CUDA="${ASR_CUDA:-off}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required but was not found in PATH" >&2
  exit 1
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python interpreter not found: $PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$VIDEO2NOTE_HOME"
mkdir -p "$VIDEO2NOTE_TMPDIR"

echo "Using runtime home: $VIDEO2NOTE_HOME"
echo "Using runtime venv: $VIDEO2NOTE_VENV"
echo "Using task temp root: $VIDEO2NOTE_TMPDIR"
echo "Creating runtime venv using $PYTHON_BIN"
uv venv --python "$PYTHON_BIN" "$VIDEO2NOTE_VENV"

UV_PYTHON="$VIDEO2NOTE_VENV/bin/python"

echo "Installing core build tools"
uv pip install --python "$UV_PYTHON" --upgrade pip setuptools wheel

case "$PADDLE_MODE" in
  cpu)
    echo "Installing PaddlePaddle CPU runtime"
    uv pip install --python "$UV_PYTHON" paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
    ;;
  gpu-cu118)
    echo "Installing PaddlePaddle GPU runtime for CUDA 11.8"
    uv pip install --python "$UV_PYTHON" paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
    ;;
  gpu-cu126)
    echo "Installing PaddlePaddle GPU runtime for CUDA 12.6"
    uv pip install --python "$UV_PYTHON" paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
    ;;
  *)
    echo "Unsupported PADDLE_MODE: $PADDLE_MODE" >&2
    exit 1
    ;;
esac

echo "Installing faster-whisper"
uv pip install --python "$UV_PYTHON" faster-whisper

echo "Installing PaddleOCR"
uv pip install --python "$UV_PYTHON" paddleocr

if [[ "$ASR_CUDA" == "pip-cu12" ]]; then
  echo "Installing CUDA 12 runtime wheels for faster-whisper"
  uv pip install --python "$UV_PYTHON" nvidia-cublas-cu12 nvidia-cudnn-cu12==9.* nvidia-cuda-nvrtc-cu12
fi

echo "Runtime setup complete"
echo "Activate with: source $ROOT_DIR/env.sh"
