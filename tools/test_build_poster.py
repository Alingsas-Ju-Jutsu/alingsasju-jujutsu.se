import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image, ImageDraw

from build_poster import ROOT, build


class PosterTest(unittest.TestCase):
    def test_both_font_styles_generate_posters(self):
        with tempfile.TemporaryDirectory() as directory:
            for style in ("condensed", "typewriter"):
                with self.subTest(style=style):
                    output = Path(directory) / f"{style}.png"
                    config = Path(directory) / "poster.yml"
                    config.write_text(yaml.safe_dump({"posters": {"test": {
                        "background": "assets/source/poster_blackbelt_blank.png",
                        "sizes": [1200], "include_website": False,
                        "include_address": True, "bottom_margin_percent": 5, "font": style,
                    }}}))
                    build(ROOT / "_data/training_schedule.yml", output, "test", config)
                    with Image.open(output) as image:
                        image.verify()
                    with Image.open(Path(directory) / "test-preview.png") as preview:
                        preview.verify()

    def test_build_generates_a_proportional_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            output = directory / "poster.png"
            preview = directory / "training-preview.png"
            build(ROOT / "_data/training_schedule.yml", output)
            with Image.open(output) as image, Image.open(preview) as thumbnail:
                self.assertEqual(thumbnail.size, (480, 600))
                self.assertEqual(image.width / image.height, thumbnail.width / thumbnail.height)

    def test_settings_control_background_optional_text_margin_and_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            background = directory / "background.png"
            Image.new("RGB", (300, 400), "navy").save(background)
            config = directory / "poster.yml"
            config.write_text(yaml.safe_dump({"posters": {"alternate": {
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

            with patch.object(ImageDraw.ImageDraw, "text", capture):
                build(ROOT / "_data/training_schedule.yml", output, "alternate", config)
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
            settings = yaml.safe_load(config.read_text())
            settings["posters"]["alternate"]["bottom_margin_percent"] = 10
            config.write_text(yaml.safe_dump(settings))
            rendered.clear()
            with patch.object(ImageDraw.ImageDraw, "text", capture):
                build(ROOT / "_data/training_schedule.yml", output, "alternate", config)
            second_y = next(position[1] for value, position, _, _ in rendered if value.startswith("TERMINSSTART"))
            with Image.open(output) as image:
                self.assertEqual(image.size, (600, 800))
            self.assertEqual(second_y, first_y - 40)

    def test_schedule_values_are_rendered_and_changes_reach_the_image(self):
        schedule = yaml.safe_load((ROOT / "_data/training_schedule.yml").read_text())
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "schedule.yml"
            output = Path(directory) / "poster.png"
            original_text = ImageDraw.ImageDraw.text
            rendered = []

            def capture(draw, position, value, **kwargs):
                rendered.append(value)
                return original_text(draw, position, value, **kwargs)

            for date, time in [("2027-01-10", "17.15"), ("15 februari 2028", "16.30")]:
                schedule["term_start"]["date"] = date
                schedule["groups"][0]["sessions"][0]["start"] = time
                source.write_text(yaml.safe_dump(schedule, allow_unicode=True))
                rendered.clear()
                with patch.object(ImageDraw.ImageDraw, "text", capture):
                    build(source, output)
                text = " ".join(rendered).upper()
                self.assertIn(date.upper(), text)
                self.assertIn(time, text)
                for group in schedule["groups"]:
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
        schedule = yaml.safe_load((ROOT / "_data/training_schedule.yml").read_text())
        schedule["term_start"]["date"] = ""
        schedule["groups"] *= 4
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "schedule.yml"
            output = Path(directory) / "poster.png"
            source.write_text(yaml.safe_dump(schedule, allow_unicode=True))
            build(source, output)
            with Image.open(output) as image:
                self.assertEqual(image.size, (1200, 1500))


if __name__ == "__main__":
    unittest.main()
