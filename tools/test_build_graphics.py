import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image, ImageDraw, ImageOps

from build_graphics import ROOT, build


class GraphicTest(unittest.TestCase):
    def test_missing_or_empty_sizes_export_only_original_and_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for extension in ("png", "svg"):
                source = directory / f"source.{extension}"
                if extension == "png":
                    Image.new("RGBA", (100, 50), (255, 0, 0, 128)).save(source)
                else:
                    source.write_text(
                        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50">'
                        '<rect width="50" height="50" fill="red"/></svg>'
                    )
                for empty_sizes in (False, True):
                    folder = directory / f"{extension}-{empty_sizes}"
                    folder.mkdir()
                    settings = {"background": str(source), "include_schedule": False}
                    if empty_sizes:
                        settings["sizes"] = []
                    config = folder / "graphics.yml"
                    config.write_text(yaml.safe_dump({"graphics": {"test": settings}}))
                    build(folder / "unused.yml", folder / "test-graphic.png", "test", config)
                    expected = {"test-preview.png"}
                    if extension == "png":
                        expected.add("test-graphic-original.png")
                        with Image.open(folder / "test-graphic-original.png") as original:
                            self.assertEqual(original.size, (100, 50))
                    self.assertEqual({p.name for p in folder.glob("*.png")}, expected)
                    self.assertEqual(list(folder.glob("*.pdf")), [])

    def test_svg_exports_preserve_dimensions_transparency_and_source(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "logo.svg"
            svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50">'
                '<rect width="50" height="50" fill="#ff0000"/></svg>'
            )
            source.write_text(svg)
            config = directory / "graphics.yml"
            config.write_text(yaml.safe_dump({"graphics": {"logo": {
                "background": str(source), "sizes": [1200, 2500],
                "include_schedule": False,
            }}}))
            output = directory / "logo-graphic.png"
            build(directory / "unused-schedule.yml", output, "logo", config)
            for name, dimensions in (
                ("logo-graphic.png", (1200, 600)),
                ("logo-graphic-2500.png", (2500, 1250)),
                ("logo-preview.png", (600, 300)),
            ):
                with Image.open(directory / name) as image:
                    self.assertEqual(image.size, dimensions)
                    self.assertEqual(image.getpixel((0, 0)), (255, 0, 0, 255))
                    self.assertEqual(image.getpixel((image.width - 1, 0))[3], 0)
            self.assertEqual(source.read_text(), svg)
            self.assertFalse((directory / "logo-graphic-original.png").exists())
            self.assertEqual(
                {path.name for path in directory.glob("*.png")},
                {"logo-graphic.png", "logo-graphic-2500.png", "logo-preview.png"},
            )
            self.assertEqual(list(directory.glob("*.pdf")), [])

    def test_raster_without_schedule_exports_only_the_artwork(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "artwork.png"
            Image.new("RGBA", (100, 50), (255, 0, 0, 128)).save(source)
            config = directory / "graphics.yml"
            config.write_text(yaml.safe_dump({"graphics": {"artwork": {
                "background": str(source), "sizes": [200], "include_schedule": False,
            }}}))
            output = directory / "generated" / "artwork.png"
            build(directory / "unused-schedule.yml", output, "artwork", config)
            with Image.open(output) as image:
                self.assertEqual(image.size, (200, 100))
                self.assertEqual(image.getpixel((0, 0)), (255, 0, 0, 128))
            self.assertEqual(list(output.parent.glob("*.pdf")), [])

    def test_svg_background_variants(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "logo.svg"
            svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">'
                '<rect width="50" height="50" fill="#ff0000"/></svg>'
            )
            source.write_text(svg)
            config = directory / "graphics.yml"
            settings = {"graphics": {"logo": {
                "background": str(source), "sizes": [120, 250],
                "include_schedule": False,
                "background_colors": {"transparent": "transparent", "white": "#ffffff"},
            }}}
            config.write_text(yaml.safe_dump(settings, sort_keys=False))
            build(directory / "unused.yml", directory / "logo-graphic.png", "logo", config)
            for suffix, width in (("", 120), ("-250", 250)):
                for color in ("transparent", "white"):
                    with Image.open(directory / f"logo-graphic{suffix}-{color}.png") as image:
                        self.assertEqual(image.size, (width, width // 2))
                        rgba = image.convert("RGBA")
                        self.assertEqual(rgba.getpixel((0, 0)), (255, 0, 0, 255))
                        right = rgba.getpixel((width - 1, 0))
                        if color == "transparent":
                            self.assertEqual(right[3], 0)
                        else:
                            self.assertEqual(right, (255, 255, 255, 255))
            self.assertEqual(source.read_text(), svg)
            self.assertFalse((directory / "logo-graphic-original.png").exists())
            self.assertFalse((directory / "logo-graphic.png").exists())
            with Image.open(directory / "logo-preview.png") as preview:
                self.assertEqual(preview.convert("RGBA").getpixel((119, 0))[3], 0)
            for colors in ({}, {"../white": "#ffffff"}, {"white": "invalid"}, ["white"]):
                settings["graphics"]["logo"]["background_colors"] = colors
                config.write_text(yaml.safe_dump(settings))
                with self.subTest(colors=colors), self.assertRaises(ValueError):
                    build(directory / "unused.yml", directory / "logo-graphic.png", "logo", config)

    def assert_pdf(self, path, width, height):
        content = path.read_bytes()
        self.assertTrue(content.startswith(b"%PDF-"))
        self.assertTrue(content.rstrip().endswith(b"%%EOF"))
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", content)), 1)
        box = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", content)
        self.assertIsNotNone(box)
        self.assertAlmostEqual(float(box[1]), width * 72 / 25.4)
        self.assertAlmostEqual(float(box[2]), height * 72 / 25.4)

    def test_both_font_styles_generate_graphics(self):
        with tempfile.TemporaryDirectory() as directory:
            for style in ("condensed", "typewriter"):
                with self.subTest(style=style):
                    output = Path(directory) / f"{style}.png"
                    config = Path(directory) / "graphics.yml"
                    config.write_text(yaml.safe_dump({"graphics": {"test": {
                        "background": "assets/source/poster_blackbelt_blank.png",
                        "sizes": [1200], "include_website": False,
                        "include_address": True, "bottom_margin_percent": 5, "font": style,
                    }}}))
                    build(ROOT / "_data/groups.yml", output, "test", config)
                    with Image.open(output) as image:
                        image.verify()
                    for suffix in ("", "-cropped"):
                        self.assert_pdf(output.with_name(f"{style}-a4{suffix}.pdf"), 210, 297)
                        self.assert_pdf(output.with_name(f"{style}-a3{suffix}.pdf"), 297, 420)
                    self.assertEqual(len(list(Path(directory).glob(f"{style}*.pdf"))), 4)
                    with Image.open(Path(directory) / "test-preview.png") as preview:
                        preview.verify()

    def test_build_generates_a_proportional_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            output = directory / "graphic.png"
            preview = directory / "training-preview.png"
            build(ROOT / "_data/groups.yml", output)
            with Image.open(output) as image, Image.open(preview) as thumbnail:
                self.assertEqual(thumbnail.size, (480, 600))
                self.assertEqual(image.width / image.height, thumbnail.width / thumbnail.height)

    def test_settings_control_background_optional_text_margin_and_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            background = directory / "background.png"
            Image.new("RGB", (300, 400), "navy").save(background)
            config = directory / "graphics.yml"
            config.write_text(yaml.safe_dump({"graphics": {"alternate": {
                "background": str(background), "sizes": [600, 900],
                "include_website": True, "include_address": False,
                "bottom_margin_percent": 5, "font": "condensed",
                "font_color": "#12ab34", "font_size": 20, "line_spacing": 8,
                "term_start_font_size": 40, "term_start_spacing": 30,
            }}}))
            output = directory / "alternate.png"
            rendered = []
            original_text = ImageDraw.ImageDraw.text

            def capture(draw, position, value, **kwargs):
                rendered.append((value, position, kwargs["fill"], kwargs["font"].size))
                return original_text(draw, position, value, **kwargs)

            with patch.object(ImageDraw.ImageDraw, "text", capture), patch(
                "build_graphics.ImageOps.fit", wraps=ImageOps.fit
            ) as fit:
                build(ROOT / "_data/groups.yml", output, "alternate", config)
            self.assertEqual(fit.call_count, 2)
            self.assertEqual([call.args[1] for call in fit.call_args_list],
                             [(1240, 1754), (1754, 2480)])
            for call in fit.call_args_list:
                self.assertEqual(call.kwargs["centering"], (0.5, 0.5))
            self.assertIn("ALINGSASJU-JUTSU.SE", [value for value, _, _, _ in rendered])
            self.assertNotIn("TENNISVÄGEN 8 · ALINGSÅS", [value for value, _, _, _ in rendered])
            self.assertTrue(all(color == "#12ab34" for _, _, color, _ in rendered))
            self.assertIn(20, [size for value, _, _, size in rendered if value.startswith("TERMINSSTART")])
            self.assertTrue(any(size == 10 for _, _, _, size in rendered))
            with Image.open(output) as image:
                self.assertEqual(image.size, (600, 800))
                self.assertEqual(image.getpixel((0, 0)), (0, 0, 128))
            first_y = next(position[1] for value, position, _, _ in rendered if value.startswith("TERMINSSTART"))
            with Image.open(directory / "alternate-900.png") as image:
                self.assertEqual(image.size[0], 900)
            with Image.open(directory / "alternate-300.png") as image:
                self.assertEqual(image.size, (300, 400))
            with Image.open(directory / "alternate-original.png") as image:
                self.assertEqual(image.size, (300, 400))
                with Image.open(directory / "alternate-300.png") as native:
                    self.assertEqual(image.tobytes(), native.tobytes())
            for suffix in ("", "-cropped"):
                self.assert_pdf(directory / f"alternate-a4{suffix}.pdf", 210, 297)
                self.assert_pdf(directory / f"alternate-a3{suffix}.pdf", 297, 420)
            self.assertEqual(len(list(directory.glob("*.pdf"))), 4)
            settings = yaml.safe_load(config.read_text())
            settings["graphics"]["alternate"]["bottom_margin_percent"] = 10
            config.write_text(yaml.safe_dump(settings))
            rendered.clear()
            with patch.object(ImageDraw.ImageDraw, "text", capture):
                build(ROOT / "_data/groups.yml", output, "alternate", config)
            second_y = next(position[1] for value, position, _, _ in rendered if value.startswith("TERMINSSTART"))
            with Image.open(output) as image:
                self.assertEqual(image.size, (600, 800))
            self.assertEqual(second_y, first_y - 40)

    def test_schedule_values_are_rendered_and_changes_reach_the_image(self):
        schedule = yaml.safe_load((ROOT / "_data/groups.yml").read_text())
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "schedule.yml"
            output = Path(directory) / "graphic.png"
            original_text = ImageDraw.ImageDraw.text
            rendered = []

            def capture(draw, position, value, **kwargs):
                rendered.append(value)
                return original_text(draw, position, value, **kwargs)

            for date, time in [("2027-01-10", "17.15"), ("15 februari 2028", "16.30")]:
                schedule["groups"]["toddlers"]["name"] = (
                    "Knattar nybörjare" if time == "16.30" else "Knattar"
                )
                schedule["term_start"]["date"] = date
                schedule["groups"]["toddlers"]["sessions"][0]["start"] = time
                source.write_text(yaml.safe_dump(schedule, allow_unicode=True))
                rendered.clear()
                with patch.object(ImageDraw.ImageDraw, "text", capture):
                    build(source, output)
                text = " ".join(rendered).upper()
                self.assertIn(date.upper(), text)
                self.assertIn(time, text)
                for group in schedule["groups"].values():
                    self.assertIn(group["name"].upper(), text)
                    self.assertIn(group["ages"].upper(), text)
                    for session in group["sessions"]:
                        self.assertIn(session["day"].upper(), text)
                        self.assertIn(session["end"], text)
                for exception in schedule["exceptions"]:
                    self.assertNotIn(str(exception["date"]), text)
                    self.assertNotIn(exception["reason"].upper(), text)
                self.assertNotIn("AVVIKELSER", text)
                with Image.open(output) as image:
                    self.assertEqual(image.format, "PNG")
                    self.assertEqual(image.width, 1200)
                    self.assertEqual(image.height, 1500)
                with Image.open(output) as image:
                    image.verify()

    def test_long_schedule_uses_original_background_size_and_blank_start_is_explicit(self):
        schedule = yaml.safe_load((ROOT / "_data/groups.yml").read_text())
        schedule["term_start"]["date"] = ""
        original_groups = list(schedule["groups"].items())
        schedule["groups"] = {
            f"{group_id}_{index}": {**group}
            for index in range(4)
            for group_id, group in original_groups
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "schedule.yml"
            output = Path(directory) / "graphic.png"
            source.write_text(yaml.safe_dump(schedule, allow_unicode=True))
            build(source, output)
            with Image.open(output) as image:
                self.assertEqual(image.size, (1200, 1500))


if __name__ == "__main__":
    unittest.main()
