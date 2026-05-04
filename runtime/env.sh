#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_HOME="${HOME:-${USERPROFILE:-}}"
if [[ -z "$USER_HOME" ]]; then
  echo "Neither HOME nor USERPROFILE is set" >&2
  return 1 2>/dev/null || exit 1
fi
VIDEO2NOTE_HOME="${VIDEO2NOTE_HOME:-$USER_HOME/video2note}"
VIDEO2NOTE_VENV="${VIDEO2NOTE_VENV:-$VIDEO2NOTE_HOME/.venv}"
TMP_BASE="${TMPDIR:-${TEMP:-${TMP:-/tmp}}}"
VIDEO2NOTE_TMPDIR="${VIDEO2NOTE_TMPDIR:-$TMP_BASE/video2note}"

if [[ ! -f "$VIDEO2NOTE_VENV/bin/activate" ]]; then
  echo "Runtime venv not found at $VIDEO2NOTE_VENV. Run setup_runtime.sh first." >&2
  return 1 2>/dev/null || exit 1
fi

mkdir -p "$VIDEO2NOTE_HOME"
mkdir -p "$VIDEO2NOTE_TMPDIR"

# shellcheck disable=SC1091
source "$VIDEO2NOTE_VENV/bin/activate"

CUDA_LIBS="$("$VIDEO2NOTE_VENV/bin/python" - <<'PY'
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

export VIDEO2NOTE_HOME
export VIDEO2NOTE_VENV
export VIDEO2NOTE_TMPDIR
export VIDEO2NOTE_RUNTIME_SCRIPTS_DIR="$ROOT_DIR"

# Backward compatibility for previous variable names.
export VIDEO2NOTE_RUNTIME_ROOT="$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR"
export VIDEO_NOTE_VENV="$VIDEO2NOTE_VENV"
export VIDEO_NOTE_RUNTIME_ROOT="$VIDEO2NOTE_RUNTIME_SCRIPTS_DIR"
