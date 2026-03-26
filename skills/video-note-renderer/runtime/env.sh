#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VIDEO_NOTE_VENV:-$ROOT_DIR/.venv}"

if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Runtime venv not found at $VENV_DIR. Run setup_runtime.sh first." >&2
  return 1 2>/dev/null || exit 1
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

CUDA_LIBS="$("$VENV_DIR/bin/python" - <<'PY'
import os
from pathlib import Path

site_packages = Path(os.environ["VIRTUAL_ENV"]) / "lib" / "python3.10" / "site-packages" / "nvidia"
parts = []
for rel in ("cublas/lib", "cudnn/lib", "cuda_nvrtc/lib"):
    path = site_packages / rel
    if path.is_dir():
        parts.append(str(path))
print(":".join(parts))
PY
)"

if [[ -n "$CUDA_LIBS" ]]; then
  export LD_LIBRARY_PATH="$CUDA_LIBS${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

export VIDEO_NOTE_RUNTIME_ROOT="$ROOT_DIR"
