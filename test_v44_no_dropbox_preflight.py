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
 def test_last_encoded_frame_restores_exact_original(self):
  import numpy as np
  from v39_progressive_drawing import frame_at,DURATION,base_without_title,derive_pencil,make_draw_map
  from v41_redraw_engine import frame_at as with_redraw
  pic=np.full((720,720,3),220,np.uint8)
  pic[50:80,530:650]=25
  clean=base_without_title(pic)
  pencil=derive_pencil(pic)
  order=make_draw_map(pic.shape)
  output=with_redraw(DURATION-1/24,pic,clean=clean,pencil=pencil,order=order)
  self.assertTrue(np.array_equal(output,pic))
 def test_fps_config_is_pinned(self):
  result=check()
  self.assertTrue(result["checks"]["recipe"])
if __name__=="__main__":unittest.main()
