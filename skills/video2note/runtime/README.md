# Runtime

Local runtime helpers for `video2note`.

Default stack:

- ASR: `faster-whisper` with `whisper-large-v3`
- OCR: `PaddleOCR` with `PP-OCRv5_server`

Model execution policy:

- Any model-backed step should prefer GPU by default.
- Whisper transcription should run on `--device cuda` whenever a usable GPU is present.
- Favor larger GPU batch sizes first and only back off when the runtime fails or runs out of memory.
- Fall back to CPU only when GPU is unavailable or demonstrably failing.

Setup:

```bash
./setup_runtime.sh
source ./env.sh
```

This creates an isolated Python 3.10 virtual environment inside:

```bash
.venv/
```

Installed packages include:

- `faster-whisper`
- `paddleocr`
- `paddlepaddle==3.2.0`

Optional environment variables before setup:

- `PADDLE_MODE=cpu|gpu-cu118|gpu-cu126`
- `ASR_CUDA=off|pip-cu12`
- `PYTHON_BIN=/usr/bin/python3.10`

Helpers:

- `transcribe_with_faster_whisper.py`
- `run_ppocrv5.py`
- `merge_chunked_transcripts.py`
- `resolve_dlpanda.py`

Example:

```bash
source ./env.sh
python transcribe_with_faster_whisper.py input.wav --model large-v3 --language zh --device cuda --batch-size 32 --output-dir out
python run_ppocrv5.py frames/ --device cpu --output-dir ocr-out
```
