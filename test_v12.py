import unittest
from v12_gate import ShotChoice,preflight
class V12Tests(unittest.TestCase):
 def test_unverified_sync_blocks(self):
  self.assertFalse(preflight([],False)["ready"])
 def test_all_verified_passes(self):
  shot=ShotChoice("walking","https://example.com",True,True,True,True,True)
  self.assertTrue(preflight([shot],True)["ready"])
 def test_vertical_crop_blocks(self):
  shot=ShotChoice("shoe","https://example.com",True,True,False,True,True)
  self.assertIn("shoe: incompatible crop or aspect ratio",preflight([shot],True)["blockers"])
 def test_motion_unchecked_blocks(self):
  shot=ShotChoice("shoe","https://example.com",True,False,True,True,True)
  self.assertFalse(preflight([shot],True)["ready"])
if __name__=="__main__": unittest.main()
