import unittest
from unittest.mock import patch
from v44_no_dropbox_preflight import check
class TestV44Preflight(unittest.TestCase):
 def test_no_source_is_safe_nonrender(self):
  result=check()
  self.assertFalse(result["ready_for_authorized_render"])
  self.assertFalse(result["rendered_video"])
  self.assertFalse(result["image_exported"])
  self.assertFalse(result["dropbox_required"])
 def test_source_disagreement_fails_closed(self):
  with patch("v44_no_dropbox_preflight.check_private_assets",side_effect=ValueError("SHA mismatch")):
   result=check("not-real.jpg","not-real.mp3")
  self.assertFalse(result["ready_for_authorized_render"])
  self.assertTrue(result["failures"])
 def test_cue_unknown_is_not_called_verified(self):
  result=check()
  self.assertTrue(any("provisional" in s for s in result["warnings"]))
 def test_fps_config_is_pinned(self):
  result=check()
  self.assertTrue(result["checks"]["recipe"])
if __name__=="__main__":unittest.main()
