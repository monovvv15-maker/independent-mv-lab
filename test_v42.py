import copy,unittest
from v42_timing_bridge import DURATION,cue_manifest,pause_bounds,warp_time,stage_state,preflight
class V42Tests(unittest.TestCase):
 def setUp(self):self.manifest=cue_manifest()
 def test_no_fake_lyric_time(self):
  self.assertTrue(preflight(self.manifest)["timing_is_provisional"])
  self.assertIsNone(self.manifest["lyric_pause"]["start_seconds"])
 def test_default_warp_identity(self):
  for t in [0,20,45,111,120,139,170,194,DURATION]:
   self.assertAlmostEqual(warp_time(t,self.manifest),t,places=4)
 def test_pause_is_truly_still(self):
  self.assertEqual(stage_state(117,self.manifest),stage_state(130,self.manifest))
 def test_realigned_pause_stops(self):
  d=copy.deepcopy(self.manifest)
  d["lyric_pause"].update(status="verified",start_seconds=143.,end_seconds=151.)
  self.assertTrue(preflight(d)["pass"])
  self.assertTrue(stage_state(146.,d)["paused"])
  self.assertFalse(stage_state(136.,d)["paused"])
 def test_missing_verified_timestamp_fails(self):
  d=copy.deepcopy(self.manifest)
  d["lyric_pause"]["status"]="verified"
  self.assertFalse(preflight(d)["pass"])
 def test_non_monotone_rejected(self):
  d=copy.deepcopy(self.manifest)
  d["lyric_pause"].update(status="verified",start_seconds=152.,end_seconds=140.)
  self.assertFalse(preflight(d)["pass"])
 def test_full_length_kept(self):
  self.assertAlmostEqual(warp_time(DURATION,self.manifest),DURATION,places=5)
 def test_no_media_was_generated(self):
  self.assertFalse(preflight(self.manifest)["video_generated"])
  self.assertFalse(preflight(self.manifest)["image_generated"])
if __name__=="__main__":unittest.main()
