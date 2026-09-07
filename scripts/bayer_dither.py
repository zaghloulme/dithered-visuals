#!/usr/bin/env python3
"""Create two-color Bayer 4x4 ordered-dither artwork from a raster image."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

BAYER_4X4 = np.array(
    [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]],
    dtype=np.float32,
)


def hex_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("colors must use six-digit hex, such as #080A0A")
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("invalid hexadecimal color") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fit", choices=("cover", "contain"), default="cover")
    parser.add_argument("--pixelation", type=int, default=2)
    parser.add_argument("--brightness", type=float, default=55.0, help="0–100; 50 is neutral")
    parser.add_argument("--contrast", type=float, default=1.16)
    parser.add_argument("--foreground", type=hex_color, default=hex_color("#080A0A"))
    parser.add_argument("--background", type=hex_color, default=hex_color("#F5F1E8"))
    parser.add_argument("--reverse", action="store_true", help="swap foreground and background colors")
    parser.add_argument("--transparent-background", action="store_true")
    parser.add_argument("--clear-side", choices=("none", "left", "right"), default="none")
    parser.add_argument("--fade-start", type=float, default=0.50)
    parser.add_argument("--fade-end", type=float, default=0.70)
    return parser.parse_args()


def fit_image(image: Image.Image, width: int, height: int, mode: str, background: tuple[int, int, int]) -> Image.Image:
    image = image.convert("RGB")
    if mode == "cover":
        return ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    contained = ImageOps.contain(image, (width, height), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), background)
    canvas.paste(contained, ((width - contained.width) // 2, (height - contained.height) // 2))
    return canvas


def main() -> None:
    args = parse_args()
    if args.pixelation < 1:
        raise SystemExit("--pixelation must be at least 1")
    if not 0 <= args.brightness <= 100:
        raise SystemExit("--brightness must be between 0 and 100")
    if args.contrast <= 0:
        raise SystemExit("--contrast must be greater than 0")
    if not 0 <= args.fade_start < args.fade_end <= 1:
        raise SystemExit("fade bounds must satisfy 0 <= start < end <= 1")

    with Image.open(args.input) as source:
        width = args.width or source.width
        height = args.height or source.height
        foreground, background = args.foreground, args.background
        if args.reverse:
            foreground, background = background, foreground
        fitted = fit_image(source, width, height, args.fit, background)

    gray = fitted.convert("L")
    block_w = (width + args.pixelation - 1) // args.pixelation
    block_h = (height + args.pixelation - 1) // args.pixelation
    reduced = gray.resize((block_w, block_h), Image.Resampling.BOX)
    tone = np.asarray(reduced, dtype=np.float32)
    tone = np.clip((tone - 128.0) * args.contrast + 128.0 + (args.brightness - 50.0) * 2.55, 0, 255)

    if args.clear_side != "none":
        x = np.linspace(0.0, 1.0, block_w, dtype=np.float32)
        reveal = np.clip((x - args.fade_start) / (args.fade_end - args.fade_start), 0.0, 1.0)
        if args.clear_side == "right":
            reveal = 1.0 - reveal
        tone = 255.0 - (255.0 - tone) * reveal[np.newaxis, :]

    matrix = np.tile(BAYER_4X4, ((block_h + 3) // 4, (block_w + 3) // 4))[:block_h, :block_w]
    threshold = ((matrix + 0.5) / 16.0) * 255.0
    use_background = tone > threshold
    fg = np.array(foreground, dtype=np.uint8)
    bg = np.array(background, dtype=np.uint8)
    rgb_small = np.where(use_background[..., np.newaxis], bg, fg)
    rgb = np.repeat(np.repeat(rgb_small, args.pixelation, axis=0), args.pixelation, axis=1)[:height, :width]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.transparent_background:
        alpha_small = np.where(use_background, 0, 255).astype(np.uint8)
        alpha = np.repeat(np.repeat(alpha_small, args.pixelation, axis=0), args.pixelation, axis=1)[:height, :width]
        Image.fromarray(np.dstack((rgb, alpha)), "RGBA").save(args.output, optimize=True)
    else:
        Image.fromarray(rgb, "RGB").save(args.output, optimize=True)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
