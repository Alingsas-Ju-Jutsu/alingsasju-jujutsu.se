import tempfile
import unittest
from pathlib import Path

from PIL import Image

from resize_article_images import resize


class ArticleImagesTest(unittest.TestCase):
    def test_resize_preserves_original_and_limits_both_axes(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for size in ((3200, 2400), (2400, 3200), (400, 300)):
                source = directory / "source.jpg"
                Image.new("RGB", size, "red").save(source)
                before = source.read_bytes()
                destination = directory / "output.jpg"
                resize(source, destination)
                with Image.open(destination) as image:
                    self.assertLessEqual(max(image.size), 1600)
                    self.assertAlmostEqual(image.width / image.height, size[0] / size[1])
                    if max(size) < 1600:
                        self.assertEqual(image.size, size)
                self.assertEqual(source.read_bytes(), before)

    def test_orientation_transparency_and_webp(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "rotated.jpg"
            exif = Image.Exif()
            exif[274] = 6
            Image.new("RGB", (2400, 1200), "blue").save(source, exif=exif)
            destination = directory / "output.jpg"
            resize(source, destination)
            with Image.open(destination) as image:
                self.assertEqual(image.size, (800, 1600))
                self.assertIsNone(image.getexif().get(274))
            for extension in ("png", "webp"):
                source = directory / f"source.{extension}"
                destination = directory / f"output.{extension}"
                Image.new("RGBA", (200, 100), (255, 0, 0, 0)).save(source)
                resize(source, destination)
                with Image.open(destination) as image:
                    self.assertEqual(image.size, (200, 100))
                    self.assertEqual(image.convert("RGBA").getpixel((0, 0))[3], 0)

    def test_invalid_images_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "broken.jpg"
            source.write_bytes(b"not an image")
            with self.assertRaises(OSError):
                resize(source, Path(directory) / "output.jpg")


if __name__ == "__main__":
    unittest.main()
