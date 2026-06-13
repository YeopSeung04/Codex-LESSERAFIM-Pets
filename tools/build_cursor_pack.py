#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CURSOR = 64
SCALE = 4
CANVAS = CURSOR * SCALE
HOTSPOT = (6, 6)
TILE = 112

TEAL = (92, 184, 183, 255)
GRID = (223, 238, 240, 255)
INK = (38, 78, 92, 255)
WHITE = (255, 255, 255, 255)
BLUE = (132, 204, 230, 255)
PINK = (255, 140, 170, 255)


ROLES = [
    "normal",
    "help",
    "working",
    "busy",
    "text",
    "handwriting",
    "link",
    "unavailable",
    "move",
    "ew-resize",
    "ns-resize",
    "nwse-resize",
    "nesw-resize",
    "precision",
    "alternate",
    "location",
    "person",
]


def clean_out_dir(path: Path) -> None:
    if path.exists():
        for child in path.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    path.mkdir(parents=True, exist_ok=True)


def crop_alpha(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    return image.crop(bbox) if bbox else image


def key_to_alpha(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    px = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = px[x, y]
            # The generated mascot source uses a cyan chroma background with
            # mild variation. Remove only cyan-dominant pixels.
            if g > 170 and b > 170 and r < 80:
                px[x, y] = (0, 0, 0, 0)
    return crop_alpha(image)


def load_source(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"Missing mascot source image: {path}")
    return key_to_alpha(Image.open(path))


def mascot_head(source: Image.Image, size: int) -> Image.Image:
    cropped = crop_alpha(source)
    left = int(cropped.width * 0.13)
    top = 0
    right = int(cropped.width * 0.87)
    bottom = int(cropped.height * 0.60)
    head = cropped.crop((left, top, right, bottom))
    head.thumbnail((size, size), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(head, ((size - head.width) // 2, (size - head.height) // 2))
    return out


def mascot_body(source: Image.Image, size: int) -> Image.Image:
    body = crop_alpha(source)
    body.thumbnail((size, size), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(body, ((size - body.width) // 2, size - body.height))
    return out


def downsample(image: Image.Image) -> Image.Image:
    return image.resize((CURSOR, CURSOR), Image.Resampling.LANCZOS)


def p(points: list[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(round(x * SCALE), round(y * SCALE)) for x, y in points]


def thick(draw: ImageDraw.ImageDraw, xy: tuple[float, float, float, float], fill=INK, width=3) -> None:
    draw.line(tuple(round(v * SCALE) for v in xy), fill=fill, width=width * SCALE)


def polygon(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill, outline=INK, width=2) -> None:
    scaled = p(points)
    draw.polygon(scaled, fill=fill)
    draw.line(scaled + [scaled[0]], fill=outline, width=width * SCALE, joint="curve")


def draw_pointer(draw: ImageDraw.ImageDraw, dx: float = 0, dy: float = 0, accent: bool = False) -> None:
    pts = [
        (5 + dx, 4 + dy),
        (35 + dx, 28 + dy),
        (23 + dx, 31 + dy),
        (30 + dx, 47 + dy),
        (21 + dx, 51 + dy),
        (14 + dx, 35 + dy),
        (5 + dx, 43 + dy),
    ]
    polygon(draw, pts, WHITE, INK, 2)
    if accent:
        draw.ellipse((29 * SCALE, 7 * SCALE, 43 * SCALE, 21 * SCALE), fill=BLUE, outline=INK, width=2 * SCALE)


def draw_busy(draw: ImageDraw.ImageDraw, cx: float, cy: float, phase: int) -> None:
    for i in range(12):
        angle = (i + phase) / 12 * math.tau
        alpha = int(55 + i * 15)
        r = 17
        x = (cx + math.cos(angle) * r) * SCALE
        y = (cy + math.sin(angle) * r) * SCALE
        radius = (2.1 + i * 0.08) * SCALE
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(38, 78, 92, alpha))


def draw_ibeam(draw: ImageDraw.ImageDraw, cx: float = 47, cy: float = 20) -> None:
    thick(draw, (cx, cy - 16, cx, cy + 16), width=4)
    thick(draw, (cx - 10, cy - 16, cx + 10, cy - 16), width=3)
    thick(draw, (cx - 10, cy + 16, cx + 10, cy + 16), width=3)
    thick(draw, (cx - 4, cy - 13, cx + 4, cy - 13), fill=WHITE, width=1)
    thick(draw, (cx - 4, cy + 13, cx + 4, cy + 13), fill=WHITE, width=1)


def draw_link(draw: ImageDraw.ImageDraw, cx: float = 47, cy: float = 19, phase: int = 0) -> None:
    offset = -1 if phase % 2 else 0
    thick(draw, (cx, cy + 12 + offset, cx, cy - 11 + offset), width=4)
    polygon(draw, [(cx, cy - 18 + offset), (cx - 10, cy - 6 + offset), (cx + 10, cy - 6 + offset)], INK, INK, 1)
    thick(draw, (cx - 1, cy + 10 + offset, cx - 1, cy - 8 + offset), fill=WHITE, width=1)


def draw_pen(draw: ImageDraw.ImageDraw, phase: int) -> None:
    offset = -1 if phase % 2 else 0
    body = [(40, 10 + offset), (55, 25 + offset), (34, 46 + offset), (25, 50 + offset), (29, 41 + offset)]
    polygon(draw, body, WHITE, INK, 2)
    thick(draw, (38, 14 + offset, 51, 27 + offset), fill=BLUE, width=4)
    thick(draw, (24, 52 + offset, 34, 48 + offset), width=3)


def draw_pin(draw: ImageDraw.ImageDraw, phase: int) -> None:
    pulse = 1 if phase in {1, 2, 3} else 0
    cx, cy = 48, 17
    draw.ellipse(
        tuple(round(v * SCALE) for v in (cx - 12 - pulse, cy - 12 - pulse, cx + 12 + pulse, cy + 12 + pulse)),
        fill=WHITE,
        outline=INK,
        width=3 * SCALE,
    )
    polygon(draw, [(cx, cy + 26 + pulse), (cx - 9, cy + 7), (cx + 9, cy + 7)], WHITE, INK, 3)
    draw.ellipse(
        tuple(round(v * SCALE) for v in (cx - 4, cy - 4, cx + 4, cy + 4)),
        fill=BLUE,
        outline=INK,
        width=1 * SCALE,
    )


def draw_person(draw: ImageDraw.ImageDraw, phase: int) -> None:
    bob = -1 if phase in {1, 2} else 0
    draw.ellipse(tuple(round(v * SCALE) for v in (43, 6 + bob, 55, 18 + bob)), fill=WHITE, outline=INK, width=3 * SCALE)
    draw.rounded_rectangle(
        tuple(round(v * SCALE) for v in (37, 22 + bob, 61, 42 + bob)),
        radius=8 * SCALE,
        fill=WHITE,
        outline=INK,
        width=3 * SCALE,
    )
    draw.arc(tuple(round(v * SCALE) for v in (42, 27 + bob, 56, 39 + bob)), 200, 340, fill=BLUE, width=2 * SCALE)


def draw_unavailable(draw: ImageDraw.ImageDraw, phase: int) -> None:
    grow = 1 if phase in {2, 3} else 0
    box = tuple(round(v * SCALE) for v in (38 - grow, 5 - grow, 63 + grow, 30 + grow))
    draw.ellipse(box, outline=INK, width=4 * SCALE)
    thick(draw, (43, 25, 58, 10), width=4)
    thick(draw, (45, 23, 56, 12), fill=WHITE, width=1)


def draw_resize(draw: ImageDraw.ImageDraw, kind: str, phase: int) -> None:
    pulse = 1 if phase in {1, 2} else 0
    cx, cy = 48, 18
    if kind == "move":
        thick(draw, (cx, cy - 18 - pulse, cx, cy + 18 + pulse), width=4)
        thick(draw, (cx - 18 - pulse, cy, cx + 18 + pulse, cy), width=4)
        arrowheads = [
            [(cx, cy - 23 - pulse), (cx - 8, cy - 12), (cx + 8, cy - 12)],
            [(cx, cy + 23 + pulse), (cx - 8, cy + 12), (cx + 8, cy + 12)],
            [(cx - 23 - pulse, cy), (cx - 12, cy - 8), (cx - 12, cy + 8)],
            [(cx + 23 + pulse, cy), (cx + 12, cy - 8), (cx + 12, cy + 8)],
        ]
    elif kind == "ew-resize":
        thick(draw, (cx - 21 - pulse, cy, cx + 21 + pulse, cy), width=4)
        arrowheads = [
            [(cx - 26 - pulse, cy), (cx - 14, cy - 8), (cx - 14, cy + 8)],
            [(cx + 26 + pulse, cy), (cx + 14, cy - 8), (cx + 14, cy + 8)],
        ]
    elif kind == "ns-resize":
        thick(draw, (cx, cy - 21 - pulse, cx, cy + 21 + pulse), width=4)
        arrowheads = [
            [(cx, cy - 26 - pulse), (cx - 8, cy - 14), (cx + 8, cy - 14)],
            [(cx, cy + 26 + pulse), (cx - 8, cy + 14), (cx + 8, cy + 14)],
        ]
    elif kind == "nwse-resize":
        thick(draw, (cx - 17 - pulse, cy - 17 - pulse, cx + 17 + pulse, cy + 17 + pulse), width=4)
        arrowheads = [
            [(cx - 22 - pulse, cy - 22 - pulse), (cx - 6, cy - 18), (cx - 18, cy - 6)],
            [(cx + 22 + pulse, cy + 22 + pulse), (cx + 6, cy + 18), (cx + 18, cy + 6)],
        ]
    else:
        thick(draw, (cx - 17 - pulse, cy + 17 + pulse, cx + 17 + pulse, cy - 17 - pulse), width=4)
        arrowheads = [
            [(cx - 22 - pulse, cy + 22 + pulse), (cx - 18, cy + 6), (cx - 6, cy + 18)],
            [(cx + 22 + pulse, cy - 22 - pulse), (cx + 18, cy - 6), (cx + 6, cy - 18)],
        ]
    for pts in arrowheads:
        polygon(draw, pts, INK, INK, 1)


def compose(role: str, source: Image.Image, phase: int) -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    bob = math.sin(phase / 6 * math.tau) * 1.25
    head = mascot_head(source, 45 * SCALE)
    body = mascot_body(source, 33 * SCALE)

    if role in {"normal", "precision"}:
        draw_pointer(draw, dx=0, dy=0, accent=role == "precision")
        canvas.alpha_composite(body, (29 * SCALE, round((28 + bob) * SCALE)))
    elif role == "alternate":
        draw_pointer(draw, dx=0, dy=0, accent=True)
        canvas.alpha_composite(head, (30 * SCALE, round((26 + bob) * SCALE)))
    elif role in {"working", "busy"}:
        canvas.alpha_composite(head, (6 * SCALE, round((15 + bob) * SCALE)))
        draw_busy(draw, 48, 18, phase)
    elif role == "text":
        canvas.alpha_composite(head, (6 * SCALE, round((16 + bob) * SCALE)))
        draw_ibeam(draw)
    elif role == "handwriting":
        canvas.alpha_composite(head, (5 * SCALE, round((17 + bob) * SCALE)))
        draw_pen(draw, phase)
    elif role == "link":
        canvas.alpha_composite(head, (6 * SCALE, round((16 + bob) * SCALE)))
        draw_link(draw, phase=phase)
    elif role == "location":
        canvas.alpha_composite(head, (5 * SCALE, round((17 + bob) * SCALE)))
        draw_pin(draw, phase)
    elif role == "person":
        canvas.alpha_composite(head, (5 * SCALE, round((17 + bob) * SCALE)))
        draw_person(draw, phase)
    elif role == "help":
        canvas.alpha_composite(head, (6 * SCALE, round((16 + bob) * SCALE)))
        draw_pointer(draw, dx=33, dy=4 + (phase % 2), accent=True)
    elif role == "unavailable":
        canvas.alpha_composite(head, (6 * SCALE, round((16 + bob) * SCALE)))
        draw_unavailable(draw, phase)
    elif role in {"move", "ew-resize", "ns-resize", "nwse-resize", "nesw-resize"}:
        canvas.alpha_composite(head, (4 * SCALE, round((18 + bob) * SCALE)))
        draw_resize(draw, role, phase)
    else:
        canvas.alpha_composite(head, (6 * SCALE, round((16 + bob) * SCALE)))

    return downsample(canvas)


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
        22,
    )
    return header + directory + data


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    pad = b"\0" if len(payload) % 2 else b""
    return tag + struct.pack("<I", len(payload)) + payload + pad


def write_cur(path: Path, image: Image.Image) -> None:
    path.write_bytes(png_to_cur_bytes(image, HOTSPOT))


def write_ani(path: Path, frames: list[Image.Image], rate_jiffies: int = 8) -> None:
    cur_frames = [png_to_cur_bytes(frame, HOTSPOT) for frame in frames]
    anih = struct.pack("<IIIIIIIII", 36, len(cur_frames), len(cur_frames), CURSOR, CURSOR, 32, 1, rate_jiffies, 1)
    rate = struct.pack("<" + "I" * len(cur_frames), *([rate_jiffies] * len(cur_frames)))
    seq = struct.pack("<" + "I" * len(cur_frames), *range(len(cur_frames)))
    fram = b"".join(riff_chunk(b"icon", frame) for frame in cur_frames)
    body = (
        riff_chunk(b"anih", anih)
        + riff_chunk(b"rate", rate)
        + riff_chunk(b"seq ", seq)
        + b"LIST"
        + struct.pack("<I", len(fram) + 4)
        + b"fram"
        + fram
    )
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
    draw.rounded_rectangle((x + 6, y + 6, x + TILE - 6, y + TILE - 6), radius=9, fill=(246, 253, 254, 245), outline=TEAL, width=2)
    sheet.alpha_composite(image, (x + 20, y + 12))
    try:
        font = ImageFont.truetype("Arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()
    draw.text((x + 10, y + TILE - 22), title, fill=INK, font=font)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pet-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--source-image", type=Path, default=None)
    args = parser.parse_args()

    source_path = args.source_image or args.pet_dir / "cursor-pack" / "source" / "mascot-base.png"
    source_bytes = source_path.read_bytes()
    source = load_source(source_path)

    clean_out_dir(args.out_dir)
    for name in ["png", "cur", "ani", "preview", "source"]:
        (args.out_dir / name).mkdir(exist_ok=True)
    source_path_out = args.out_dir / "source" / "mascot-base.png"
    source_path_out.write_bytes(source_bytes)

    role_first_frames: dict[str, Image.Image] = {}
    for role in ROLES:
        frames = [compose(role, source, phase) for phase in range(6)]
        role_first_frames[role] = frames[0]
        frames[0].save(args.out_dir / "png" / f"{role}.png")
        write_cur(args.out_dir / "cur" / f"{role}.cur", frames[0])
        write_ani(args.out_dir / "ani" / f"{role}.ani", frames, rate_jiffies=8 if role != "busy" else 6)
        frames[0].save(
            args.out_dir / "preview" / f"{role}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=80,
            loop=0,
            disposal=2,
        )

    rows = math.ceil(len(ROLES) / 4)
    sheet = Image.new("RGBA", (TILE * 4, TILE * rows), (255, 255, 255, 255))
    draw_grid_bg(sheet)
    for i, role in enumerate(ROLES):
        draw_tile(sheet, i, role, role_first_frames[role])
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, 10), fill=TEAL)
    draw.rectangle((0, sheet.height - 10, sheet.width, sheet.height), fill=TEAL)
    sheet.save(args.out_dir / "preview" / "cursor-sheet.png")


if __name__ == "__main__":
    main()
