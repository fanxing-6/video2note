#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge chunked faster-whisper outputs into one SRT/JSON.")
    parser.add_argument("chunk_dir", type=Path, help="Directory containing per-chunk JSON/SRT outputs")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for merged outputs")
    parser.add_argument("--stem", type=str, default="merged", help="Output filename stem")
    return parser.parse_args()


def format_ts(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000.0)))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main() -> int:
    args = parse_args()
    chunk_dir = args.chunk_dir
    output_dir = args.output_dir or chunk_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(chunk_dir.glob("chunk_*.json"))
    if not json_files:
        raise SystemExit(f"No chunk JSON files found under {chunk_dir}")

    merged_segments = []
    model = None
    language = None
    language_probability = None
    runtime_device = None
    runtime_compute_type = None
    total_duration = 0.0

    for path in json_files:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if model is None:
            model = payload.get("model")
            language = payload.get("language")
            language_probability = payload.get("language_probability")
            runtime_device = payload.get("runtime_device")
            runtime_compute_type = payload.get("runtime_compute_type")
        for segment in payload.get("segments", []):
            merged_segments.append(segment)
        total_duration = max(total_duration, payload.get("duration", 0.0) or 0.0)

    merged_segments.sort(key=lambda item: (item.get("start", 0.0), item.get("id", 0)))
    for index, segment in enumerate(merged_segments):
        segment["id"] = index

    srt_path = output_dir / f"{args.stem}.srt"
    json_path = output_dir / f"{args.stem}.json"

    with srt_path.open("w", encoding="utf-8") as srt_file:
        for idx, segment in enumerate(merged_segments, start=1):
            srt_file.write(f"{idx}\n")
            srt_file.write(f"{format_ts(segment['start'])} --> {format_ts(segment['end'])}\n")
            srt_file.write(f"{segment['text'].strip()}\n\n")

    merged_payload = {
        "model": model,
        "language": language,
        "language_probability": language_probability,
        "duration": total_duration,
        "runtime_device": runtime_device,
        "runtime_compute_type": runtime_compute_type,
        "segments": merged_segments,
    }
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(merged_payload, fh, ensure_ascii=False, indent=2)

    print(f"Wrote {srt_path}")
    print(f"Wrote {json_path}")
    print(f"Merged segments: {len(merged_segments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
