#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from faster_whisper import BatchedInferencePipeline, WhisperModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe media with faster-whisper.")
    parser.add_argument("input", type=Path, help="Path to local audio or video file")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="Directory for transcript outputs")
    parser.add_argument("--stem", type=str, default=None, help="Override output filename stem")
    parser.add_argument("--model", default="large-v3", help="Whisper model name")
    parser.add_argument("--language", default="zh", help="Language hint")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--compute-type", default=None, help="Override compute type")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--best-of", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=None, help="Use batched inference with this batch size")
    parser.add_argument("--chunk-length", type=int, default=None, help="Chunk length in seconds for batched inference")
    parser.add_argument("--min-silence-ms", type=int, default=500)
    parser.add_argument("--log-progress", action="store_true")
    parser.add_argument("--condition-on-previous-text", action="store_true")
    return parser.parse_args()


def format_ts(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000.0)))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def select_runtime(device: str, compute_type: str | None) -> list[tuple[str, str]]:
    if device == "cpu":
        return [("cpu", compute_type or "int8")]
    if device == "cuda":
        return [("cuda", compute_type or "float16")]
    candidates: list[tuple[str, str]] = []
    if compute_type:
        candidates.append(("cuda", compute_type))
        candidates.append(("cpu", compute_type))
    else:
        candidates.extend([("cuda", "float16"), ("cuda", "int8_float16"), ("cpu", "int8")])
    return candidates


def load_model(model_name: str, device: str, compute_type: str | None) -> tuple[WhisperModel, str, str]:
    last_error: Exception | None = None
    for candidate_device, candidate_compute in select_runtime(device, compute_type):
        try:
            model = WhisperModel(model_name, device=candidate_device, compute_type=candidate_compute)
            return model, candidate_device, candidate_compute
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(
                f"Whisper runtime failed for device={candidate_device} compute_type={candidate_compute}: {exc}",
                file=sys.stderr,
            )
    raise RuntimeError(f"Unable to load faster-whisper model {model_name}: {last_error}")


def transcribe_with_optional_batching(
    model: WhisperModel,
    args: argparse.Namespace,
    runtime_device: str,
):
    chunk_length = args.chunk_length
    if chunk_length is None and runtime_device == "cuda":
        chunk_length = 30

    kwargs = dict(
        language=args.language,
        beam_size=args.beam_size,
        best_of=args.best_of,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": args.min_silence_ms},
        condition_on_previous_text=args.condition_on_previous_text,
        chunk_length=chunk_length,
        log_progress=args.log_progress,
    )

    requested_batch_size = args.batch_size
    if requested_batch_size is None:
        requested_batch_size = 32 if runtime_device == "cuda" else 1

    if requested_batch_size <= 1:
        return model.transcribe(str(args.input), **kwargs), 1

    pipeline = BatchedInferencePipeline(model=model)
    batch_size = requested_batch_size
    last_error: Exception | None = None
    while batch_size >= 1:
        try:
            segments_iter, info = pipeline.transcribe(str(args.input), batch_size=batch_size, **kwargs)
            return (segments_iter, info), batch_size
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if runtime_device != "cuda" or batch_size == 1:
                break
            print(f"Batched inference failed at batch_size={batch_size}: {exc}", file=sys.stderr)
            batch_size //= 2

    raise RuntimeError(f"Unable to transcribe with batched inference: {last_error}")


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.stem or args.input.stem

    model, runtime_device, runtime_compute = load_model(args.model, args.device, args.compute_type)
    (segments_iter, info), effective_batch_size = transcribe_with_optional_batching(model, args, runtime_device)
    segments = list(segments_iter)

    srt_path = output_dir / f"{stem}.srt"
    json_path = output_dir / f"{stem}.json"

    with srt_path.open("w", encoding="utf-8") as srt_file:
        for idx, segment in enumerate(segments, start=1):
            text = segment.text.strip()
            srt_file.write(f"{idx}\n")
            srt_file.write(f"{format_ts(segment.start)} --> {format_ts(segment.end)}\n")
            srt_file.write(f"{text}\n\n")

    payload = {
        "model": args.model,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": getattr(info, "duration", None),
        "duration_after_vad": getattr(info, "duration_after_vad", None),
        "runtime_device": runtime_device,
        "runtime_compute_type": runtime_compute,
        "batch_size": effective_batch_size,
        "segments": [],
    }

    for segment in segments:
        payload["segments"].append(
            {
                "id": segment.id,
                "seek": segment.seek,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "avg_logprob": segment.avg_logprob,
                "no_speech_prob": segment.no_speech_prob,
                "words": [
                    {
                        "start": word.start,
                        "end": word.end,
                        "word": word.word,
                        "probability": word.probability,
                    }
                    for word in (segment.words or [])
                ],
            }
        )

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, ensure_ascii=False, indent=2)

    print(f"Wrote {srt_path}")
    print(f"Wrote {json_path}")
    print(f"Runtime: device={runtime_device} compute_type={runtime_compute} batch_size={effective_batch_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
