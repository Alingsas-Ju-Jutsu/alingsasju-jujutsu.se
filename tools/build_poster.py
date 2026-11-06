"""Render the downloadable training poster from the site's shared schedule."""

import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONTS = {
    "condensed": ("DejaVuSansCondensed.ttf", "DejaVuSansCondensed-Bold.ttf"),
    "typewriter": ("DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf"),
    "antonio": ("Antonio.ttf", "Antonio.ttf"),
}


def build(schedule_path, output, poster_name="training", config_path=None, preview_output=None):
    config_path = config_path or ROOT / "_data/poster.yml"
    with config_path.open(encoding="utf-8") as source:
        posters = yaml.safe_load(source)["posters"]
    if poster_name not in posters:
        raise ValueError(f"Unknown poster {poster_name!r}; choose from {', '.join(posters)}.")
    config = posters[poster_name]
    preview_output = preview_output or output.with_name(f"{poster_name}-preview.png")
    font_color = config.get("font_color", "#ffffff")
    if not isinstance(font_color, str) or len(font_color) != 7 or font_color[0] != "#":
        raise ValueError("Poster font_color must be a hex color in #RRGGBB format.")
    try:
        int(font_color[1:], 16)
    except ValueError as error:
        raise ValueError("Poster font_color must be a hex color in #RRGGBB format.") from error
    font_size = config.get("font_size", 25)
    line_spacing = config.get("line_spacing", 14)
    term_start_font_size = config.get("term_start_font_size", 45)
    term_start_spacing = config.get("term_start_spacing", 45)
    for name, value in (("font_size", font_size), ("line_spacing", line_spacing),
                        ("term_start_font_size", term_start_font_size),
                        ("term_start_spacing", term_start_spacing)):
        if not isinstance(value, int) or value < 0 or (name.endswith("font_size") and value == 0):
            qualifier = "positive" if name.endswith("font_size") else "non-negative"
            raise ValueError(f"Poster {name} must be a {qualifier} integer.")
    font_style = config["font"]
    if font_style not in FONTS:
        raise ValueError(f"Unknown poster font {font_style!r}; choose condensed or typewriter.")
    regular, heavy = FONTS[font_style]
    font_directory = ROOT / "assets/fonts" if font_style == "antonio" else Path(
        "/usr/share/fonts/truetype/dejavu"
    )
    background_path = ROOT / config["background"]
    sizes = config["sizes"]
    if not sizes or any(not isinstance(size, int) or size <= 0 for size in sizes):
        raise ValueError("Poster sizes must be a non-empty list of positive pixel widths.")
    with Image.open(background_path) as background:
        original_width = background.width
    if original_width not in sizes:
        sizes = [*sizes, original_width]
    margin_percent = config["bottom_margin_percent"]
    if not 0 <= margin_percent <= 100:
        raise ValueError("Poster bottom_margin_percent must be between 0 and 100.")
    with schedule_path.open(encoding="utf-8") as source:
        schedule = yaml.safe_load(source)
    if not schedule["groups"]:
        raise ValueError("The poster requires at least one training group.")
    schedule["schedule"] = [
        {
            **group,
            "name": group.get("name") or group_id,
        }
        for group_id, group in schedule["groups"].items()
    ]

    base_width = 1200

    def render(width, destination):
        scale = width / base_width
        with Image.open(background_path) as original:
            image = original.convert("RGBA").resize(
                (width, round(original.height * width / original.width)), Image.Resampling.LANCZOS
            )
        draw = ImageDraw.Draw(image)

        def text(value, y, size=34, bold=False, color=None, measure=False,
                 center=None, max_width=None):
            size = round(size * scale)
            color = font_color if color is None else color
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
                y += size + round(line_spacing * scale)
            return y

        columns = min(3, len(schedule["schedule"]))
        column_width = (base_width - 100) / columns

        def group_rows(y, measure=False, bottom_spacing=45):
            for offset in range(0, len(schedule["schedule"]), columns):
                bottom = y
                for column, group in enumerate(schedule["schedule"][offset:offset + columns]):
                    options = {
                        "center": 50 + column_width * (column + 0.5),
                        "max_width": column_width - 35,
                        "measure": measure,
                    }
                    end = text(f'{group["name"]} {group["ages"]}'.upper(), y,
                               size=round(font_size * 1.2), bold=True, **options)
                    end += round(12 * scale)
                    for session in group["sessions"]:
                        end = text(
                            f'{session["day"]} {session["start"]}–{session["end"]}'.upper(),
                            end, size=font_size, **options,
                        )
                    bottom = max(bottom, end)
                y = bottom + round(45 * scale)
            return y - round(45 * scale) + round(bottom_spacing * scale)

        rows = []
        start = schedule["term_start"]
        date = str(start["date"]).strip() or "Datum meddelas snart."
        rows.append((f'{start["title"]} {date}'.upper(), term_start_font_size, False))
        if config["include_address"]:
            rows.extend([("", 14, False), ("TENNISVÄGEN 8 · ALINGSÅS", 23, False)])
        if config["include_website"]:
            rows.extend([("", 14, False), ("ALINGSASJU-JUTSU.SE", 23, False)])

    # Measure the schedule first so it can be anchored to the image's bottom.
        groups_end = group_rows(0, measure=True, bottom_spacing=term_start_spacing)
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
        group_rows(y, bottom_spacing=term_start_spacing)
        y += groups_end
        for value, size, bold in rows:
            y = text(value, y, size, bold) if value else y + round(size * scale)
        destination.parent.mkdir(parents=True, exist_ok=True)
        poster = image.convert("RGB")
        poster.save(destination, optimize=True)
        if width == original_width:
            poster.save(output.with_name(f"{output.stem}-original.png"), optimize=True)
        if width == max(sizes):
            for paper, millimeters in (("a4", (210, 297)), ("a3", (297, 420))):
                page_size = tuple(round(length / 25.4 * 150) for length in millimeters)
                fitted = ImageOps.contain(poster, page_size, Image.Resampling.LANCZOS)
                page = Image.new("RGB", page_size, "white")
                page.paste(fitted, ((page.width - fitted.width) // 2,
                                    (page.height - fitted.height) // 2))
                cropped = ImageOps.fit(
                    poster, page_size, method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5),
                )
                for suffix, version in (("", page), ("-cropped", cropped)):
                    version.save(
                        output.with_name(f"{output.stem}-{paper}{suffix}.pdf"),
                        "PDF", dpi=(page.width * 25.4 / millimeters[0],
                                    page.height * 25.4 / millimeters[1]), quality=95,
                    )
        if width == sizes[0]:
            preview = poster.copy()
            preview.thumbnail((600, 600), Image.Resampling.LANCZOS)
            preview_output.parent.mkdir(parents=True, exist_ok=True)
            preview.save(preview_output, optimize=True)
        print(f"Generated {destination}: {width}×{image.height}, {len(schedule['schedule'])} groups")

    for index, width in enumerate(sizes):
        destination = output if index == 0 else output.with_name(
            f"{output.stem}-{width}{output.suffix}"
        )
        render(width, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=ROOT / "_data/groups.yml")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/generated/training-poster.png")
    parser.add_argument("--poster", help="Poster name from _data/poster.yml (defaults to all posters)")
    args = parser.parse_args()
    if args.poster:
        build(args.schedule, args.output, args.poster,
              preview_output=args.output.with_name(f"{args.poster}-preview.png"))
    else:
        with (ROOT / "_data/poster.yml").open(encoding="utf-8") as source:
            poster_names = yaml.safe_load(source)["posters"]
        for poster_name in poster_names:
            output = ROOT / "assets/generated" / f"{poster_name}-poster.png"
            build(
            	args.schedule,
            	output,
            	poster_name,
                preview_output=output.with_name(f"{poster_name}-preview.png")
            )
