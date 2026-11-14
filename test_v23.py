import unittest
from v23_prelaunch import SHOTS,validate
from v23_video_only import ffmpeg_command
class Tests(unittest.TestCase):
 def test_six(self):self.assertEqual(len(SHOTS),6)
 def test_30s(self):self.assertEqual(sum(x[-1] for x in SHOTS),30)
 def test_metadata(self):self.assertEqual(validate(),[])
 def test_no_audio(self):self.assertIn('-an',ffmpeg_command(['x']*6,'out','ffmpeg'))
 def test_expected_frames(self):self.assertIn('fps=30',ffmpeg_command(['x']*6,'out','ffmpeg')[ffmpeg_command(['x']*6,'out','ffmpeg').index('-filter_complex')+1])
 def test_short_rejected(self):
  with self.assertRaises(ValueError):ffmpeg_command(['x']*3,'out','ffmpeg')
if __name__=='__main__':unittest.main()
