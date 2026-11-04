"""Render the downloadable training poster from the site's shared schedule."""

import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = {
    "condensed": ("DejaVuSansCondensed.ttf", "DejaVuSansCondensed-Bold.ttf"),
    "typewriter": ("DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf"),
}


def build(schedule_path, output, poster_name="training", config_path=None):
    config_path = config_path or ROOT / "_data/poster.yml"
    with config_path.open(encoding="utf-8") as source:
        posters = yaml.safe_load(source)["posters"]
    if poster_name not in posters:
        raise ValueError(f"Unknown poster {poster_name!r}; choose from {', '.join(posters)}.")
    config = posters[poster_name]
    font_style = config["font"]
    if font_style not in FONTS:
        raise ValueError(f"Unknown poster font {font_style!r}; choose condensed or typewriter.")
    regular, heavy = FONTS[font_style]
    font_directory = Path("/usr/share/fonts/truetype/dejavu")
    background_path = ROOT / config["background"]
    sizes = config["sizes"]
    if not sizes or any(not isinstance(size, int) or size <= 0 for size in sizes):
        raise ValueError("Poster sizes must be a non-empty list of positive pixel widths.")
    margin_percent = config["bottom_margin_percent"]
    if not 0 <= margin_percent <= 100:
        raise ValueError("Poster bottom_margin_percent must be between 0 and 100.")
    with schedule_path.open(encoding="utf-8") as source:
        schedule = yaml.safe_load(source)
    if not schedule["groups"]:
        raise ValueError("The poster requires at least one training group.")

    base_width = 1200

    def render(width, destination):
        scale = width / base_width
        with Image.open(background_path) as original:
            image = original.convert("RGBA").resize(
                (width, round(original.height * width / original.width)), Image.Resampling.LANCZOS
            )
        draw = ImageDraw.Draw(image)

        def text(value, y, size=34, bold=False, color="white", measure=False,
                 center=None, max_width=None):
            size = round(size * scale)
            center = width / 2 if center is None else center * scale
            max_width = (base_width - 120) if max_width is None else max_width
            max_width *= scale
            font = ImageFont.truetype(str(font_directory / (heavy if bold else regular)), size)
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
                    draw.text((center, round(y)), line, font=font, fill=color, anchor="mt")
                y += size + round(14 * scale)
            return y

        columns = min(3, len(schedule["groups"]))
        column_width = (base_width - 100) / columns

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
                    end += round(12 * scale)
                    for session in group["sessions"]:
                        end = text(
                            f'{session["day"]} {session["start"]}–{session["end"]}'.upper(),
                            end, size=25, **options,
                        )
                    bottom = max(bottom, end)
                y = bottom + round(45 * scale)
            return y

        rows = []
        start = schedule["term_start"]
        date = str(start["date"]).strip() or "Datum meddelas snart."
        rows.append((f'{start["title"]} {date}'.upper(), 45, False))
        if config["include_address"]:
            rows.extend([("", 14, False), ("TENNISVÄGEN 8 · ALINGSÅS", 23, False)])
        if config["include_website"]:
            rows.extend([("", 14, False), ("ALINGSASJU-JUTSU.SE", 23, False)])

    # Measure the schedule first so it can be anchored to the image's bottom.
        groups_end = group_rows(0, measure=True)
        end = groups_end
        for value, size, bold in rows:
            end = text(value, end, size, bold, measure=True) if value else end + round(size * scale)
        margin = round(image.height * margin_percent / 100)
        y = image.height - margin - end
        if y < 0:
            raise ValueError(
                f"Schedule does not fit the {width}px-wide background with "
                f"a {margin_percent}% bottom margin."
            )
        group_rows(y)
        y += groups_end
        for value, size, bold in rows:
            y = text(value, y, size, bold) if value else y + round(size * scale)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(destination, optimize=True)
        print(f"Generated {destination}: {width}×{image.height}, {len(schedule['groups'])} groups")

    for index, width in enumerate(sizes):
        destination = output if index == 0 else output.with_name(
            f"{output.stem}-{width}{output.suffix}"
        )
        render(width, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=ROOT / "_data/training_schedule.yml")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/generated/training-poster.png")
    parser.add_argument("--poster", default="training", help="Poster name from _data/poster.yml")
    args = parser.parse_args()
    build(args.schedule, args.output, args.poster)
