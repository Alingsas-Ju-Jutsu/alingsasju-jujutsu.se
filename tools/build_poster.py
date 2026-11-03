"""Render the downloadable training poster from the site's shared schedule."""

import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def build(schedule_path, output):
    with schedule_path.open(encoding="utf-8") as source:
        schedule = yaml.safe_load(source)
    if not schedule["groups"]:
        raise ValueError("The poster requires at least one training group.")

    width = 1200
    # Retain the original artwork above its baked-in timetable until a blank
    # background is available. None of the old dates or times are retained.
    original = Image.open(ROOT / "assets/archive/2d416e4f25efdeb4af7b8391.png")
    artwork = original.crop((0, 0, original.width, round(original.height * 0.72)))
    artwork = artwork.resize(
        (width, round(artwork.height * width / artwork.width)),
        Image.Resampling.LANCZOS,
    ).convert("RGB")
    image = artwork.copy()
    draw = ImageDraw.Draw(image)

    def text(value, y, size=34, bold=False, color="white", measure=False,
             center=600, max_width=1080):
        font = ImageFont.truetype(BOLD if bold else FONT, size)
        lines = []
        line = ""
        for word in str(value).split():
            candidate = f"{line} {word}".strip()
            if draw.textlength(word, font=font) > max_width:
                raise ValueError(f"Poster word is too wide: {word}")
            if line and draw.textlength(candidate, font=font) > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        for line in lines:
            if not measure:
                draw.text((center, y), line, font=font, fill=color, anchor="mt")
            y += size + 14
        return y

    panel_y = artwork.height
    columns = min(3, len(schedule["groups"]))
    column_width = (width - 100) / columns

    def group_rows(y, measure=False):
        for offset in range(0, len(schedule["groups"]), columns):
            bottom = y
            for column, group in enumerate(schedule["groups"][offset:offset + columns]):
                options = {
                    "center": 50 + column_width * (column + 0.5),
                    "max_width": column_width - 35,
                    "measure": measure,
                }
                end = text(f'{group["name"]} {group["ages"]}'.upper(), y,
                           size=30, bold=True, **options)
                end += 12
                for session in group["sessions"]:
                    end = text(
                        f'{session["day"]} {session["start"]}–{session["end"]}'.upper(),
                        end, size=25, **options,
                    )
                bottom = max(bottom, end)
            y = bottom + 45
        return y

    rows = []
    start = schedule["term_start"]
    date = str(start["date"]).strip() or "Datum meddelas snart."
    rows.append((f'{start["title"]} {date}'.upper(), 45, False))
    rows.extend([
        ("", 14, False),
        ("TENNISVÄGEN 8 · ALINGSÅS", 23, False),
        ("WWW.ALINGSASJU-JUTSU.SE", 23, False),
    ])

    # Measure with the same renderer, then extend the canvas for longer schedules.
    groups_end = group_rows(panel_y + 35, measure=True)
    end = groups_end
    for value, size, bold in rows:
        end = text(value, end, size, bold, measure=True) if value else end + size
    height = max(1500, end + 50)
    canvas = Image.new("RGB", (width, height), "#17212b")
    canvas.paste(artwork, (0, 0))
    image = canvas
    draw = ImageDraw.Draw(image)
    group_rows(panel_y + 35)
    y = groups_end
    for value, size, bold in rows:
        y = text(value, y, size, bold) if value else y + size
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, optimize=True)
    print(f"Generated {output}: {width}×{height}, {len(schedule['groups'])} groups")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=ROOT / "_data/training_schedule.yml")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/generated/training-poster.png")
    args = parser.parse_args()
    build(args.schedule, args.output)
