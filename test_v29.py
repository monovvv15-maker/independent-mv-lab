import unittest
from v29_script_qa import check
class V29Tests(unittest.TestCase):
 def test_canonical_has_seven_chapters(self):self.assertEqual(check()["chapters"],7)
 def test_no_fabricated_photo_inventory(self):self.assertEqual(check()["photo_inventory"],"not independently verified")
 def test_full_length(self):self.assertAlmostEqual(check()["total_seconds"],199.872,places=3)
 def test_no_premature_render(self):self.assertFalse(check()["video_generated"])
 def test_final_canonical_valid(self):self.assertEqual(check()["errors"],[])
if __name__=="__main__":unittest.main()
