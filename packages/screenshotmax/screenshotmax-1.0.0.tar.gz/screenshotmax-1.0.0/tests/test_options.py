# test_options.py
import unittest
from screenshotmax.options import ScreenshotOptions
from screenshotmax.enums import ImageFormat

class TestScreenshotOptions(unittest.TestCase):
  def test_to_dict_includes_only_non_none_values(self):
    options = ScreenshotOptions(
      url="https://example.com",
      format=ImageFormat.PNG,
      full_page=True
    )
    data = options.to_dict()
    self.assertEqual(data["url"], "https://example.com")
    self.assertEqual(data["format"], "png")
    self.assertEqual(data["full_page"], True)
    self.assertNotIn("viewport_device", data)

if __name__ == "__main__":
  unittest.main()
