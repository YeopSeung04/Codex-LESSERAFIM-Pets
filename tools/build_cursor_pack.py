#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence


TILE = 96
CURSOR = 64
HOTSPOT = (6, 6)
TEAL = (92, 184, 183, 255)
GRID = (223, 238, 240, 255)
INK = (42, 94, 112, 255)
WHITE = (255, 255, 255, 255)
PINK = (255, 130, 165, 255)


def load_gif_frames(path: Path) -> list[Image.Image]:
    image = Image.open(path)
    frames = []
    for frame in ImageSequence.Iterator(image):
        frames.append(frame.convert("RGBA"))
    return frames


def crop_alpha(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    return image.crop(bbox) if bbox else image


def fit(image: Image.Image, size: int, pad: int = 4) -> Image.Image:
    cropped = crop_alpha(image)
    cropped.thumbnail((size - pad * 2, size - pad * 2), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(cropped, ((size - cropped.width) // 2, size - cropped.height - pad))
    return out


def head(image: Image.Image, size: int) -> Image.Image:
    cropped = crop_alpha(image)
    # Top-heavy crop keeps the glasses and hair loops readable at cursor size.
    top = 0
    bottom = int(cropped.height * 0.62)
    left = int(cropped.width * 0.12)
    right = int(cropped.width * 0.88)
    cropped = cropped.crop((left, top, right, bottom))
    cropped.thumbnail((size - 10, size - 10), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(cropped, ((size - cropped.width) // 2, (size - cropped.height) // 2))
    return out


def draw_arrow(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    pts = [
        (x, y),
        (x + int(24 * scale), y + int(18 * scale)),
        (x + int(14 * scale), y + int(21 * scale)),
        (x + int(20 * scale), y + int(34 * scale)),
        (x + int(13 * scale), y + int(37 * scale)),
        (x + int(8 * scale), y + int(24 * scale)),
        (x, y + int(31 * scale)),
    ]
    draw.polygon(pts, fill=WHITE, outline=INK)
    draw.line(pts + [pts[0]], fill=INK, width=2)


def draw_symbol(draw: ImageDraw.ImageDraw, kind: str, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "text":
        draw.line((cx, y0, cx, y1), fill=INK, width=4)
        draw.line((cx - 9, y0, cx + 9, y0), fill=INK, width=3)
        draw.line((cx - 9, y1, cx + 9, y1), fill=INK, width=3)
    elif kind == "link":
        draw.line((cx, y0 + 8, cx, y1 - 8), fill=INK, width=4)
        draw.polygon([(cx, y0), (cx - 9, y0 + 11), (cx + 9, y0 + 11)], fill=INK)
    elif kind == "move":
        draw.line((cx, y0, cx, y1), fill=INK, width=4)
        draw.line((x0, cy, x1, cy), fill=INK, width=4)
        draw.polygon([(cx, y0), (cx - 8, y0 + 10), (cx + 8, y0 + 10)], fill=INK)
        draw.polygon([(cx, y1), (cx - 8, y1 - 10), (cx + 8, y1 - 10)], fill=INK)
        draw.polygon([(x0, cy), (x0 + 10, cy - 8), (x0 + 10, cy + 8)], fill=INK)
        draw.polygon([(x1, cy), (x1 - 10, cy - 8), (x1 - 10, cy + 8)], fill=INK)
    elif kind == "ew":
        draw.line((x0, cy, x1, cy), fill=INK, width=4)
        draw.polygon([(x0, cy), (x0 + 10, cy - 8), (x0 + 10, cy + 8)], fill=INK)
        draw.polygon([(x1, cy), (x1 - 10, cy - 8), (x1 - 10, cy + 8)], fill=INK)
    elif kind == "ns":
        draw.line((cx, y0, cx, y1), fill=INK, width=4)
        draw.polygon([(cx, y0), (cx - 8, y0 + 10), (cx + 8, y0 + 10)], fill=INK)
        draw.polygon([(cx, y1), (cx - 8, y1 - 10), (cx + 8, y1 - 10)], fill=INK)
    elif kind == "diag1":
        draw.line((x0, y1, x1, y0), fill=INK, width=4)
        draw.polygon([(x1, y0), (x1 - 13, y0 + 2), (x1 - 2, y0 + 13)], fill=INK)
        draw.polygon([(x0, y1), (x0 + 13, y1 - 2), (x0 + 2, y1 - 13)], fill=INK)
    elif kind == "diag2":
        draw.line((x0, y0, x1, y1), fill=INK, width=4)
        draw.polygon([(x0, y0), (x0 + 13, y0 + 2), (x0 + 2, y0 + 13)], fill=INK)
        draw.polygon([(x1, y1), (x1 - 13, y1 - 2), (x1 - 2, y1 - 13)], fill=INK)
    elif kind == "unavailable":
        draw.ellipse((x0 + 3, y0 + 3, x1 - 3, y1 - 3), outline=INK, width=4)
        draw.line((x0 + 11, y1 - 11, x1 - 11, y0 + 11), fill=INK, width=4)
    elif kind == "busy":
        for i in range(12):
            angle = i / 12
            px = cx + int(18 * __import__("math").cos(angle * 6.283))
            py = cy + int(18 * __import__("math").sin(angle * 6.283))
            alpha = int(80 + i * 14)
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(42, 94, 112, alpha))


def make_cursor_frame(base: Image.Image, role: str, symbol: str | None = None, use_head: bool = False) -> Image.Image:
    out = Image.new("RGBA", (CURSOR, CURSOR), (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)
    if role in {"normal", "precision"}:
        draw_arrow(draw, 2, 2, 0.9)
        pet = fit(base, 38, 0)
        out.alpha_composite(pet, (24, 24))
    elif use_head:
        pet = head(base, 50)
        out.alpha_composite(pet, (7, 11))
        if symbol:
            draw_symbol(draw, symbol, (38, 2, 62, 26))
    else:
        pet = fit(base, 54, 0)
        out.alpha_composite(pet, (5, 8))
        if symbol:
            draw_symbol(draw, symbol, (34, 4, 62, 32))
    return out


def png_to_cur_bytes(image: Image.Image, hotspot: tuple[int, int]) -> bytes:
    import io

    png = io.BytesIO()
    image.save(png, format="PNG")
    data = png.getvalue()
    header = struct.pack("<HHH", 0, 2, 1)
    directory = struct.pack(
        "<BBBBHHII",
        image.width if image.width < 256 else 0,
        image.height if image.height < 256 else 0,
        0,
        0,
        hotspot[0],
        hotspot[1],
        len(data),
        6 + 16,
    )
    return header + directory + data


def write_cur(path: Path, image: Image.Image, hotspot: tuple[int, int] = HOTSPOT) -> None:
    path.write_bytes(png_to_cur_bytes(image, hotspot))


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    pad = b"\0" if len(payload) % 2 else b""
    return tag + struct.pack("<I", len(payload)) + payload + pad


def write_ani(path: Path, frames: list[Image.Image], rate_jiffies: int = 8) -> None:
    cur_frames = [png_to_cur_bytes(frame, HOTSPOT) for frame in frames]
    anih = struct.pack("<IIIIIIIII", 36, len(cur_frames), len(cur_frames), CURSOR, CURSOR, 32, 1, rate_jiffies, 1)
    rate = struct.pack("<" + "I" * len(cur_frames), *([rate_jiffies] * len(cur_frames)))
    seq = struct.pack("<" + "I" * len(cur_frames), *range(len(cur_frames)))
    fram = b"".join(riff_chunk(b"icon", frame) for frame in cur_frames)
    body = riff_chunk(b"anih", anih) + riff_chunk(b"rate", rate) + riff_chunk(b"seq ", seq) + b"LIST" + struct.pack("<I", len(fram) + 4) + b"fram" + fram
    path.write_bytes(b"RIFF" + struct.pack("<I", len(body) + 4) + b"ACON" + body)


def draw_grid_bg(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    for x in range(0, image.width, 16):
        draw.line((x, 0, x, image.height), fill=GRID)
    for y in range(0, image.height, 16):
        draw.line((0, y, image.width, y), fill=GRID)


def draw_tile(sheet: Image.Image, idx: int, title: str, image: Image.Image) -> None:
    col = idx % 4
    row = idx // 4
    x = col * TILE
    y = row * TILE
    draw = ImageDraw.Draw(sheet)
    draw.rounded_rectangle((x + 5, y + 5, x + TILE - 5, y + TILE - 5), radius=8, fill=(245, 252, 253, 245), outline=TEAL, width=2)
    sheet.alpha_composite(image, (x + 16, y + 10))
    try:
        font = ImageFont.truetype("Arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()
    draw.text((x + 10, y + TILE - 18), title, fill=INK, font=font)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pet-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    previews = args.pet_dir / "qa" / "previews"
    idle = load_gif_frames(previews / "idle.gif")
    running = load_gif_frames(previews / "running.gif")
    waiting = load_gif_frames(previews / "waiting.gif")
    review = load_gif_frames(previews / "review.gif")
    failed = load_gif_frames(previews / "failed.gif")
    waving = load_gif_frames(previews / "waving.gif")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "png").mkdir(exist_ok=True)
    (args.out_dir / "cur").mkdir(exist_ok=True)
    (args.out_dir / "ani").mkdir(exist_ok=True)
    (args.out_dir / "preview").mkdir(exist_ok=True)

    roles = {
        "normal": make_cursor_frame(idle[0], "normal"),
        "help": make_cursor_frame(waiting[1], "help", "link", True),
        "working": make_cursor_frame(running[0], "working", "busy", True),
        "busy": make_cursor_frame(running[1], "busy", "busy", True),
        "text": make_cursor_frame(review[0], "text", "text", True),
        "link": make_cursor_frame(waving[1], "link", "link", True),
        "unavailable": make_cursor_frame(failed[3], "unavailable", "unavailable", True),
        "move": make_cursor_frame(idle[1], "move", "move", True),
        "ew-resize": make_cursor_frame(idle[0], "ew", "ew", True),
        "ns-resize": make_cursor_frame(idle[0], "ns", "ns", True),
        "nwse-resize": make_cursor_frame(idle[0], "diag1", "diag1", True),
        "nesw-resize": make_cursor_frame(idle[0], "diag2", "diag2", True),
    }

    for name, image in roles.items():
        image.save(args.out_dir / "png" / f"{name}.png")
        write_cur(args.out_dir / "cur" / f"{name}.cur", image)

    write_ani(args.out_dir / "ani" / "working.ani", [make_cursor_frame(frame, "working", "busy", True) for frame in running[:6]])
    write_ani(args.out_dir / "ani" / "busy.ani", [make_cursor_frame(frame, "busy", "busy", True) for frame in running[:6]], rate_jiffies=6)
    write_ani(args.out_dir / "ani" / "waiting.ani", [make_cursor_frame(frame, "waiting", "link", True) for frame in waiting[:6]], rate_jiffies=10)

    sheet = Image.new("RGBA", (TILE * 4, TILE * 4), (255, 255, 255, 255))
    draw_grid_bg(sheet)
    for i, (name, image) in enumerate(roles.items()):
        draw_tile(sheet, i, name, image)
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, 10), fill=TEAL)
    draw.rectangle((0, sheet.height - 10, sheet.width, sheet.height), fill=TEAL)
    sheet.save(args.out_dir / "preview" / "cursor-sheet.png")

    for name in ["working", "busy", "waiting"]:
        frames = []
        source = running if name in {"working", "busy"} else waiting
        symbol = "busy" if name in {"working", "busy"} else "link"
        for frame in source[:6]:
            frames.append(make_cursor_frame(frame, name, symbol, True))
        frames[0].save(
            args.out_dir / "preview" / f"{name}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=90,
            loop=0,
            disposal=2,
        )


if __name__ == "__main__":
    main()
