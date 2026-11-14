import unittest
from v16_prelaunch import readiness
class V16Tests(unittest.TestCase):
 def test_default_blocks_video(self):self.assertFalse(readiness()["ready"])
 def test_missing_neighborhood_fails(self):
  r=readiness(voice_start_seconds=15.5, private_audio_present=True, full_clips_present=True,frame_review_complete=True)
  self.assertTrue(any("06_neighborhood" in x for x in r["blockers"]))
 def test_all_inputs_ready(self):
  clips=[{"scene":"a","candidate":"clip","role":"sun","status":"approved"}]
  self.assertTrue(readiness(clips,voice_start_seconds=15.5,private_audio_present=True,full_clips_present=True,frame_review_complete=True)["ready"])
if __name__=="__main__":unittest.main()
