#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paddleocr import PaddleOCR


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PaddleOCR PP-OCRv5 on images.")
    parser.add_argument("input", type=Path, help="Image file or directory")
    parser.add_argument("--output-dir", type=Path, default=Path("ocr-output"))
    parser.add_argument("--lang", default="ch")
    parser.add_argument("--device", choices=["auto", "cpu", "gpu"], default="auto")
    parser.add_argument("--use-doc-orientation-classify", action="store_true")
    parser.add_argument("--use-doc-unwarping", action="store_true")
    parser.add_argument("--use-textline-orientation", action="store_true")
    return parser.parse_args()


def list_images(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    return []


def resolve_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import paddle

        return "gpu" if paddle.device.is_compiled_with_cuda() else "cpu"
    except Exception:  # noqa: BLE001
        return "cpu"


def main() -> int:
    args = parse_args()
    images = list_images(args.input)
    if not images:
        print(f"No images found under {args.input}", file=sys.stderr)
        return 1

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    device = resolve_device(args.device)
    ocr = PaddleOCR(
        lang=args.lang,
        device=device,
        use_doc_orientation_classify=args.use_doc_orientation_classify,
        use_doc_unwarping=args.use_doc_unwarping,
        use_textline_orientation=args.use_textline_orientation,
        text_detection_model_name="PP-OCRv5_server_det",
        text_recognition_model_name="PP-OCRv5_server_rec",
    )

    for image_path in images:
        print(f"Processing {image_path}")
        results = ocr.predict(str(image_path))
        for result in results:
            result.print()
            result.save_to_json(str(output_dir))
            result.save_to_img(str(output_dir))

    print(f"Saved OCR outputs under {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
