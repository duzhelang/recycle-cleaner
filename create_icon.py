from __future__ import annotations

import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow is required: pip install pillow")

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "logo.ico"


def create_icon() -> None:
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r = size // 3

    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(32, 128, 240, 255))

    inner = int(r * 0.55)
    draw.rectangle((cx - inner, cy - inner, cx + inner, cy + inner), fill=(255, 255, 255, 255))

    draw.rectangle((cx - int(inner * 0.5), cy - int(inner * 1.25), cx + int(inner * 0.5), cy - inner), fill=(255, 255, 255, 255))

    OUT.parent.mkdir(exist_ok=True)
    img.save(OUT, format="ICO", sizes=[(256, 256)])
    print(f"[OK] Icon created: {OUT}")


if __name__ == "__main__":
    create_icon()
