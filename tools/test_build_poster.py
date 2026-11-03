import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image, ImageChops, ImageDraw

from build_poster import ROOT, build


class PosterTest(unittest.TestCase):
    def test_both_font_styles_generate_posters(self):
        with tempfile.TemporaryDirectory() as directory:
            for style in ("condensed", "typewriter"):
                with self.subTest(style=style):
                    output = Path(directory) / f"{style}.png"
                    build(ROOT / "_data/training_schedule.yml", output, font_style=style)
                    with Image.open(output) as image:
                        image.verify()

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
                    with Image.open(ROOT / "assets/archive/2d416e4f25efdeb4af7b8391.png") as original:
                        artwork = original.crop(
                            (0, 0, original.width, round(original.height * 0.72))
                        )
                        artwork = artwork.resize(
                            (1200, round(artwork.height * 1200 / artwork.width)),
                            Image.Resampling.LANCZOS,
                        ).convert("RGB")
                        self.assertIsNone(ImageChops.difference(
                            image.crop((0, 0, artwork.width, artwork.height)),
                            artwork,
                        ).getbbox())
                with Image.open(output) as image:
                    image.verify()

    def test_long_schedule_expands_and_blank_start_is_explicit(self):
        schedule = yaml.safe_load((ROOT / "_data/training_schedule.yml").read_text())
        schedule["term_start"]["date"] = ""
        schedule["groups"] *= 4
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "schedule.yml"
            output = Path(directory) / "poster.png"
            source.write_text(yaml.safe_dump(schedule, allow_unicode=True))
            build(source, output)
            with Image.open(output) as image:
                self.assertGreater(image.height, 2000)


if __name__ == "__main__":
    unittest.main()
