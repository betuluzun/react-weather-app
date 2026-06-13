#!/usr/bin/env python3
"""Generate weather app logo and icon assets."""

from pathlib import Path

from PIL import Image, ImageDraw

PUBLIC = Path(__file__).resolve().parents[1] / "public"

# Brand palette
PRIMARY = (83, 166, 250)
SECONDARY = (124, 183, 241)
TERTIARY = (137, 190, 243)
LIGHT_BLUE = (198, 222, 255)
WHITE = (255, 255, 255)
SUN = (255, 183, 77)
SUN_DARK = (255, 152, 0)
BG_DARK = (45, 120, 210)
BG_LIGHT = (83, 166, 250)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def radial_gradient(size, inner, outer):
    img = Image.new("RGBA", (size, size))
    pixels = img.load()
    center = (size - 1) / 2
    max_dist = center * 1.15
    for y in range(size):
        for x in range(size):
            dist = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
            t = min(dist / max_dist, 1.0)
            pixels[x, y] = (*lerp(inner, outer, t), 255)
    return img


def draw_weather_icon(draw, size, offset=(0, 0), scale=1.0):
    ox, oy = offset
    s = scale

    sun_cx = int((size * 0.36 + ox) * s + (1 - s) * size * 0.5)
    sun_cy = int((size * 0.34 + oy) * s + (1 - s) * size * 0.5)
    sun_r = int(size * 0.13 * s)

    for angle in range(0, 360, 45):
        import math

        rad = math.radians(angle)
        x1 = sun_cx + math.cos(rad) * (sun_r + size * 0.03 * s)
        y1 = sun_cy + math.sin(rad) * (sun_r + size * 0.03 * s)
        x2 = sun_cx + math.cos(rad) * (sun_r + size * 0.08 * s)
        y2 = sun_cy + math.sin(rad) * (sun_r + size * 0.08 * s)
        draw.line([(x1, y1), (x2, y2)], fill=SUN, width=max(2, int(size * 0.018 * s)))

    draw.ellipse(
        [
            sun_cx - sun_r,
            sun_cy - sun_r,
            sun_cx + sun_r,
            sun_cy + sun_r,
        ],
        fill=SUN,
    )

    cloud_cx = int(size * 0.54 + ox)
    cloud_cy = int(size * 0.58 + oy)
    cloud_w = int(size * 0.42 * s)
    cloud_h = int(size * 0.22 * s)
    bubble_r = int(size * 0.11 * s)

    cloud_color = WHITE
    shadow = LIGHT_BLUE

    bubbles = [
        (cloud_cx - cloud_w // 3, cloud_cy - bubble_r // 2, bubble_r),
        (cloud_cx, cloud_cy - bubble_r, int(bubble_r * 1.15)),
        (cloud_cx + cloud_w // 3, cloud_cy - bubble_r // 3, int(bubble_r * 0.95)),
    ]

    draw.rounded_rectangle(
        [
            cloud_cx - cloud_w // 2,
            cloud_cy,
            cloud_cx + cloud_w // 2,
            cloud_cy + cloud_h,
        ],
        radius=int(size * 0.06 * s),
        fill=shadow,
    )

    for bx, by, br in bubbles:
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=shadow)

    draw.rounded_rectangle(
        [
            cloud_cx - cloud_w // 2,
            cloud_cy - int(size * 0.01 * s),
            cloud_cx + cloud_w // 2,
            cloud_cy + cloud_h - int(size * 0.02 * s),
        ],
        radius=int(size * 0.06 * s),
        fill=cloud_color,
    )

    for bx, by, br in bubbles:
        draw.ellipse(
            [bx - br, by - br - int(size * 0.02 * s), bx + br, by + br - int(size * 0.02 * s)],
            fill=cloud_color,
        )

    drop_positions = [
        (cloud_cx - cloud_w // 5, cloud_cy + cloud_h + int(size * 0.06 * s), 0.55),
        (cloud_cx + cloud_w // 8, cloud_cy + cloud_h + int(size * 0.1 * s), 0.7),
        (cloud_cx + cloud_w // 3, cloud_cy + cloud_h + int(size * 0.05 * s), 0.45),
    ]

    for dx, dy, factor in drop_positions:
        dr = int(size * 0.035 * factor * s)
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr * 1.4], fill=SECONDARY)
        draw.ellipse(
            [dx - dr // 2, dy - dr // 3, dx - dr // 6, dy + dr // 4],
            fill=LIGHT_BLUE,
        )


def render_icon(size, background="gradient", padding=0.12):
    img = radial_gradient(size, BG_LIGHT, BG_DARK) if background == "gradient" else Image.new(
        "RGBA", (size, size), (*WHITE, 255)
    )
    draw = ImageDraw.Draw(img)

    inner = int(size * (1 - padding * 2))
    scale = inner / size
    offset = size * padding
    draw_weather_icon(draw, size, offset=(offset, offset), scale=scale)
    return img


def save_png(img, path):
    if img.mode == "RGBA":
        img.save(path, "PNG", optimize=True)
    else:
        img.convert("RGB").save(path, "PNG", optimize=True)


def save_ico(img, path):
  sizes = [16, 32, 48, 64, 128, 256]
  icons = [img.resize((s, s), Image.Resampling.LANCZOS) for s in sizes]
  icons[0].save(path, format="ICO", sizes=[(s, s) for s in sizes])


def main():
    PUBLIC.mkdir(parents=True, exist_ok=True)

    logo_512 = render_icon(512, background="gradient", padding=0.1)
    save_png(logo_512, PUBLIC / "logo.png")

    logo_192 = logo_512.resize((192, 192), Image.Resampling.LANCZOS)
    save_png(logo_192, PUBLIC / "logo192.png")

    maskable_512 = render_icon(512, background="gradient", padding=0.18)
    save_png(maskable_512, PUBLIC / "maskable_icon.png")
    save_png(maskable_512, PUBLIC / "maskable_icon_x512.png")

    for dim in (48, 72, 96, 128, 192, 384):
        resized = maskable_512.resize((dim, dim), Image.Resampling.LANCZOS)
        save_png(resized, PUBLIC / f"maskable_icon_x{dim}.png")

    favicon_source = logo_512.resize((256, 256), Image.Resampling.LANCZOS)
    save_ico(favicon_source, PUBLIC / "favicon.ico")

    print("Generated logo assets in", PUBLIC)


if __name__ == "__main__":
    main()
