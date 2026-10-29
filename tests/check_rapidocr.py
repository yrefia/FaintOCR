"""Environment self-check for the workspace Python + RapidOCR setup.

Renders a small image with known text, runs the bundled RapidOCR engine on it
and fails when the expected text is not recognised. Run with the workspace
virtual environment:

    .venv\\Scripts\\python.exe tests\\check_rapidocr.py
"""
from __future__ import annotations

import os
import platform
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"

EXPECTED = "rapidocr"
CANVAS = (1000, 260)


def _font(size: int):
    from PIL import ImageFont

    for name in ("arial.ttf", "segoeui.ttf"):
        candidate = FONT_DIR / name
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def _distribution(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not installed"


def _render_target(path: Path) -> str:
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", CANVAS, "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 40), "RapidOCR self-check 2026", fill="black", font=_font(56))
    chinese_font = FONT_DIR / "msyh.ttc"
    if chinese_font.is_file():
        draw.text((40, 140), "中文自检：OCR 环境正常", fill="black",
                  font=ImageFont.truetype(str(chinese_font), 48))
    image.save(path)
    return str(path)


def main() -> int:
    print(f"python      : {sys.version.split()[0]} ({platform.machine()})")
    print(f"executable  : {sys.executable}")
    for name in ("rapidocr", "onnxruntime", "opencv-python-headless", "numpy", "pillow"):
        print(f"{name:<12}: {_distribution(name)}")

    from rapidocr import RapidOCR

    engine = RapidOCR(params={"Global.log_level": "warning"})
    output_dir = ROOT / "build" / "rapidocr-check"
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = _render_target(output_dir / "target.png")
    print(f"image       : {image_path}")
    result = engine(image_path)

    texts = list(result.txts) if result.txts is not None else []
    boxes = list(result.boxes) if result.boxes is not None else []
    scores = list(result.scores) if result.scores is not None else []
    print(f"boxes       : {len(boxes)}")
    print(f"detected    : {texts}")
    if scores:
        print(f"scores      : {[round(float(score), 4) for score in scores]}")

    joined = " ".join(texts).lower()
    if EXPECTED not in joined:
        print(f"FAIL: expected '{EXPECTED}' in recognised text", file=sys.stderr)
        return 1
    print("OK: RapidOCR recognised the rendered text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
