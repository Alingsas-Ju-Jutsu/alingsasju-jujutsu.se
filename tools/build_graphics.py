"""Generate downloadable graphics, optionally with the shared training schedule."""

import argparse
import re
import subprocess
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONTS = {
    "condensed": ("DejaVuSansCondensed.ttf", "DejaVuSansCondensed-Bold.ttf"),
    "typewriter": ("DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf"),
    "antonio": ("Antonio.ttf", "Antonio.ttf"),
}


def build_graphic(background, output, preview_output, sizes, background_colors=None):
    output.parent.mkdir(parents=True, exist_ok=True)
    original_output = output.with_name(f"{output.stem}-original.png")
    is_svg = background.suffix.lower() == ".svg"

    def render(destination, width=None, color="transparent"):
        if is_svg:
            command = ["rsvg-convert", "--output", str(destination)]
            if width is not None:
                command.extend(["--width", str(width)])
            if color != "transparent":
                command.extend(["--background-color", color])
            subprocess.run([*command, str(background)], check=True)
        else:
            with Image.open(background) as source:
                image = source.convert("RGBA")
                if width is not None:
                    image = image.resize(
                        (width, round(image.height * width / image.width)),
                        Image.Resampling.LANCZOS,
                    )
                image.save(destination, optimize=True)

    widths = sizes
    if not sizes:
        destination = preview_output if is_svg else original_output
        destination.parent.mkdir(parents=True, exist_ok=True)
        render(destination)
        with Image.open(destination) as image:
            image.thumbnail((600, 600), Image.Resampling.LANCZOS)
            preview_output.parent.mkdir(parents=True, exist_ok=True)
            image.save(preview_output, optimize=True)
        return
    if not is_svg:
        render(original_output)
        with Image.open(original_output) as original:
            original_width = original.width
        if original_width not in sizes:
            widths = [*sizes, original_width]
    for index, width in enumerate(widths):
        destination = output if index == 0 else output.with_name(
            f"{output.stem}-{width}{output.suffix}"
        )
        for variant_index, (name, color) in enumerate(
            (background_colors or {"": "transparent"}).items()
        ):
            variant_output = destination.with_name(
                f"{destination.stem}-{name}.png"
            ) if name else destination
            render(variant_output, width, color)
            if index == 0 and variant_index == 0:
                with Image.open(variant_output) as image:
                    image.thumbnail((600, 600), Image.Resampling.LANCZOS)
                    preview_output.parent.mkdir(parents=True, exist_ok=True)
                    image.save(preview_output, optimize=True)
            print(f"Generated {variant_output}: {width}px wide")


def build_grading_times(background, output, preview_output, sizes, schedule, config):
    if background.suffix.lower() == ".svg":
        raise ValueError("Grading-time graphics require a raster background.")
    grading_groups = [
        (group.get("name") or group_id, group["grading"])
        for group_id, group in schedule["groups"].items()
        if group.get("grading", {}).get("date") or group.get("grading", {}).get("time")
    ]
    if not grading_groups:
        raise ValueError("The schedule has no grading dates or times to render.")
    font_style = config.get("font", "antonio")
    if font_style not in FONTS:
        raise ValueError(f"Unknown graphic font {font_style!r}; choose from {', '.join(FONTS)}.")
    color = config.get("font_color", "#ffffff")
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Graphic font_color must be a hex color in #RRGGBB format.")
    bottom_text = config.get("bottom_text", {})
    if isinstance(bottom_text, str):
        bottom_text = {"text": bottom_text}
    if not isinstance(bottom_text, dict):
        raise ValueError("Graphic bottom_text must be a string or mapping of text settings.")
    footer = bottom_text.get("text", "")
    if not isinstance(footer, str):
        raise ValueError("Graphic bottom_text.text must be a string.")
    footer_size = bottom_text.get("font_size", 24)
    footer_spacing = bottom_text.get("line_spacing", 8)
    footer_color = bottom_text.get("font_color", color)
    for name, value in (("font_size", footer_size), ("line_spacing", footer_spacing)):
        if not isinstance(value, int) or value < 0 or (name == "font_size" and value == 0):
            raise ValueError(f"Graphic bottom_text.{name} must be a positive font size or non-negative spacing.")
    if not isinstance(footer_color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", footer_color):
        raise ValueError("Graphic bottom_text.font_color must be a hex color in #RRGGBB format.")
    footer_font_style = bottom_text.get("font", font_style)
    if footer_font_style not in FONTS:
        raise ValueError(f"Unknown bottom text font {footer_font_style!r}; choose from {', '.join(FONTS)}.")
    margin_percent = config.get("bottom_margin_percent", 5)
    if not isinstance(margin_percent, (int, float)) or not 0 <= margin_percent <= 100:
        raise ValueError("Graphic bottom_margin_percent must be between 0 and 100.")
    title = config.get("grading_title", "GRADERINGSTIDER")
    title_size = config.get("grading_title_font_size", 48)
    group_size = config.get("grading_group_font_size", 32)
    detail_size = config.get("grading_detail_font_size", 28)
    spacing = config.get("line_spacing", 12)
    for name, value in (("grading_title_font_size", title_size),
                        ("grading_group_font_size", group_size),
                        ("grading_detail_font_size", detail_size), ("line_spacing", spacing)):
        if not isinstance(value, int) or value < 0 or (name.endswith("font_size") and value == 0):
            raise ValueError(f"Graphic {name} must be a positive font size or non-negative spacing.")
    with Image.open(background) as source:
        original_width = source.width
    requested_sizes = list(sizes)
    render_sizes = requested_sizes or [original_width]
    if original_width not in render_sizes:
        render_sizes.append(original_width)
    output.parent.mkdir(parents=True, exist_ok=True)

    def render(width, destination):
        scale = width / 1200
        with Image.open(background) as source:
            image = source.convert("RGBA").resize(
                (width, round(source.height * width / source.width)), Image.Resampling.LANCZOS
            )
        draw = ImageDraw.Draw(image)

        def draw_text(value, y, size, style, text_color, center=width / 2,
                      line_spacing=spacing):
            font_file = FONTS[style][1]
            directory = ROOT / "assets/fonts" if style == "antonio" else Path(
                "/usr/share/fonts/truetype/dejavu"
            )
            font = ImageFont.truetype(str(directory / font_file), max(1, round(size * scale)))
            draw.text((center, round(y)), value, font=font, fill=text_color, anchor="mt")
            return y + font.size + round(line_spacing * scale)

        title_end = title_size + spacing
        group_height = group_size + spacing + detail_size + spacing
        columns = min(3, len(grading_groups))
        group_rows = [grading_groups[index:index + columns]
                      for index in range(0, len(grading_groups), columns)]
        footer_height = 0
        if footer:
            footer_lines = footer.splitlines()
            footer_height = len(footer_lines) * (footer_size + footer_spacing)
        total_height = round((title_end + len(group_rows) * group_height + footer_height) * scale)
        margin = round(image.height * margin_percent / 100)
        y = image.height - margin - total_height
        if y < 0:
            raise ValueError(f"Grading times do not fit the {width}px-wide background.")
        y = draw_text(str(title).upper(), y, title_size, font_style, color)
        column_width = width / columns
        for row in group_rows:
            row_bottom = y
            for column, (group_name, grading) in enumerate(row):
                center = column_width * (column + 0.5)
                display_name = str(group_name)
                if grading.get("is_preliminary"):
                    display_name = f"{display_name} (prel)"
                group_y = draw_text(
                    display_name.upper(), y, group_size, font_style, color, center
                )
                date = str(grading.get("date", "")).strip()
                time = str(grading.get("time", "")).strip()
                details = " · ".join(value for value in (date, time) if value)
                row_bottom = max(row_bottom, draw_text(
                    details, group_y, detail_size, font_style, color, center
                ))
            y = row_bottom + round(spacing * scale)
        if footer:
            y += round(spacing * scale)
            for line in footer.splitlines():
                y = draw_text(
                    line, y, footer_size, footer_font_style, footer_color,
                    line_spacing=footer_spacing,
                )
        image.convert("RGB").save(destination, optimize=True)
        if width == original_width:
            image.convert("RGB").save(
                output.with_name(f"{output.stem}-original.png"), optimize=True
            )
        if width == render_sizes[0]:
            preview = image.convert("RGB")
            preview.thumbnail((600, 600), Image.Resampling.LANCZOS)
            preview_output.parent.mkdir(parents=True, exist_ok=True)
            preview.save(preview_output, optimize=True)
        print(f"Generated {destination}: {width}×{image.height}, {len(grading_groups)} grading groups")

    for index, width in enumerate(render_sizes):
        destination = output if index == 0 else output.with_name(
            f"{output.stem}-{width}{output.suffix}"
        )
        if not requested_sizes:
            destination = output.with_name(f"{output.stem}-original{output.suffix}")
        render(width, destination)


def build(schedule_path, output, graphic_name="training", config_path=None, preview_output=None):
    config_path = config_path or ROOT / "_data/graphics.yml"
    with config_path.open(encoding="utf-8") as source:
        graphics = yaml.safe_load(source)["graphics"]
    if graphic_name not in graphics:
        raise ValueError(f"Unknown graphic {graphic_name!r}; choose from {', '.join(graphics)}.")
    config = graphics[graphic_name]
    preview_output = preview_output or output.with_name(f"{graphic_name}-preview.png")
    background_path = ROOT / config["background"]
    sizes = config.get("sizes", [])
    if not isinstance(sizes, list) or any(
        not isinstance(size, int) or isinstance(size, bool) or size <= 0 for size in sizes
    ):
        raise ValueError("Graphic sizes must be a list of positive pixel widths.")
    export_sizes = bool(sizes)
    include_schedule = config.get("include_schedule", True)
    if not isinstance(include_schedule, bool):
        raise ValueError("Graphic include_schedule must be true or false.")
    include_grading_times = config.get("include_grading_times", False)
    if not isinstance(include_grading_times, bool):
        raise ValueError("Graphic include_grading_times must be true or false.")
    if include_grading_times:
        if include_schedule:
            raise ValueError("include_grading_times requires include_schedule: false.")
        with schedule_path.open(encoding="utf-8") as source:
            schedule = yaml.safe_load(source)
        build_grading_times(background_path, output, preview_output, sizes, schedule, config)
        return
    background_colors = config.get("background_colors")
    if background_colors is not None:
        if include_schedule or background_path.suffix.lower() != ".svg":
            raise ValueError("background_colors requires SVG graphics without a schedule.")
        if not isinstance(background_colors, dict) or not background_colors:
            raise ValueError("background_colors must be a non-empty mapping of names to colors.")
        for name, color in background_colors.items():
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                raise ValueError("Background names must use lowercase letters, digits and hyphens.")
            if not isinstance(color, str):
                raise ValueError("Background colors must be transparent or hex colors (#RRGGBB).")
            if color != "transparent":
                if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                    raise ValueError("Background colors must be transparent or hex colors (#RRGGBB).")
    if not include_schedule:
        build_graphic(background_path, output, preview_output, sizes, background_colors)
        return
    if background_path.suffix.lower() == ".svg":
        raise ValueError("SVG graphics require include_schedule: false.")
    font_color = config.get("font_color", "#ffffff")
    if not isinstance(font_color, str) or len(font_color) != 7 or font_color[0] != "#":
        raise ValueError("Graphic font_color must be a hex color in #RRGGBB format.")
    try:
        int(font_color[1:], 16)
    except ValueError as error:
        raise ValueError("Graphic font_color must be a hex color in #RRGGBB format.") from error
    font_size = config.get("font_size", 25)
    line_spacing = config.get("line_spacing", 14)
    term_start_font_size = config.get("term_start_font_size", 45)
    term_start_spacing = config.get("term_start_spacing", 45)
    for name, value in (("font_size", font_size), ("line_spacing", line_spacing),
                        ("term_start_font_size", term_start_font_size),
                        ("term_start_spacing", term_start_spacing)):
        if not isinstance(value, int) or value < 0 or (name.endswith("font_size") and value == 0):
            qualifier = "positive" if name.endswith("font_size") else "non-negative"
            raise ValueError(f"Graphic {name} must be a {qualifier} integer.")
    font_style = config["font"]
    if font_style not in FONTS:
        raise ValueError(f"Unknown graphic font {font_style!r}; choose condensed or typewriter.")
    regular, heavy = FONTS[font_style]
    font_directory = ROOT / "assets/fonts" if font_style == "antonio" else Path(
        "/usr/share/fonts/truetype/dejavu"
    )
    with Image.open(background_path) as background:
        original_width = background.width
    if original_width not in sizes:
        sizes = [*sizes, original_width]
    margin_percent = config["bottom_margin_percent"]
    if not 0 <= margin_percent <= 100:
        raise ValueError("Graphic bottom_margin_percent must be between 0 and 100.")
    with schedule_path.open(encoding="utf-8") as source:
        schedule = yaml.safe_load(source)
    if not schedule["groups"]:
        raise ValueError("The graphic requires at least one training group.")
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
                    raise ValueError(f"Graphic word is too wide: {word}")
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
        graphic = image.convert("RGB")
        graphic.save(destination, optimize=True)
        if width == original_width:
            graphic.save(output.with_name(f"{output.stem}-original.png"), optimize=True)
        if export_sizes and width == max(sizes):
            for paper, millimeters in (("a4", (210, 297)), ("a3", (297, 420))):
                page_size = tuple(round(length / 25.4 * 150) for length in millimeters)
                fitted = ImageOps.contain(graphic, page_size, Image.Resampling.LANCZOS)
                page = Image.new("RGB", page_size, "white")
                page.paste(fitted, ((page.width - fitted.width) // 2,
                                    (page.height - fitted.height) // 2))
                cropped = ImageOps.fit(
                    graphic, page_size, method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5),
                )
                for suffix, version in (("", page), ("-cropped", cropped)):
                    version.save(
                        output.with_name(f"{output.stem}-{paper}{suffix}.pdf"),
                        "PDF", dpi=(page.width * 25.4 / millimeters[0],
                                    page.height * 25.4 / millimeters[1]), quality=95,
                    )
        if width == sizes[0]:
            preview = graphic.copy()
            preview.thumbnail((600, 600), Image.Resampling.LANCZOS)
            preview_output.parent.mkdir(parents=True, exist_ok=True)
            preview.save(preview_output, optimize=True)
        print(f"Generated {destination}: {width}×{image.height}, {len(schedule['schedule'])} groups")

    for index, width in enumerate(sizes):
        destination = output if index == 0 else output.with_name(
            f"{output.stem}-{width}{output.suffix}"
        )
        if not export_sizes:
            destination = output.with_name(f"{output.stem}-original.png")
        render(width, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=ROOT / "_data/groups.yml")
    parser.add_argument("--output", type=Path, help="PNG path (requires --graphic)")
    parser.add_argument("--graphic", help="Graphic name from _data/graphics.yml (defaults to all graphics)")
    args = parser.parse_args()
    if args.output and not args.graphic:
        parser.error("--output requires --graphic")
    if args.graphic:
        output = args.output or ROOT / "assets/generated" / f"{args.graphic}-graphic.png"
        build(args.schedule, output, args.graphic)
    else:
        with (ROOT / "_data/graphics.yml").open(encoding="utf-8") as source:
            graphic_names = yaml.safe_load(source)["graphics"]
        for graphic_name in graphic_names:
            output = ROOT / "assets/generated" / f"{graphic_name}-graphic.png"
            build(args.schedule, output, graphic_name)
