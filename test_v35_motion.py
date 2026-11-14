import unittest
from v35_motion_screen import frame_change,score
class MotionTests(unittest.TestCase):
 def test_equal(self):self.assertEqual(frame_change(bytes([7,7]),bytes([7,7])),0)
 def test_difference(self):self.assertEqual(frame_change(bytes([0]),bytes([255])),1)
 def test_changed_video(self):
  frames=[bytes([i]*4) for i in [0,10,20,20,20,20,40]]
  self.assertGreaterEqual(score(frames)["motion_sample_count"],1)
 def test_no_claim_stop(self):self.assertIn("requires full-motion review",score([bytes([0]),bytes([0])])["note"])
if __name__=="__main__":unittest.main()
