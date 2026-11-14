import unittest
from v31_style_engine import filter_chain,validate
class V31Tests(unittest.TestCase):
 def test_no_render(self):self.assertFalse(validate()["video_generated"])
 def test_real_jacket_palette_logged(self):self.assertEqual(validate()["reference_rgb"]["sky_median_rgb"],[189,192,201])
 def test_can_compile_filter(self):
  f=filter_chain()
  self.assertIn("eq=contrast=",f)
  self.assertIn("noise=alls=",f)
 def test_seven_chapters(self):self.assertEqual(len(validate()["chapters"]),7)
 def test_no_fake_approval(self):self.assertFalse(validate()["music_word_timestamps_verified"])
if __name__=="__main__":unittest.main()
