import unittest
from v28_full_renderer import trim_command,concat_command,source_offset
class V28RendererTests(unittest.TestCase):
 def test_720p_frame(self):
  cmd=trim_command('ffmpeg','in.mp4','out.mp4',1.0,6.25)
  self.assertIn('-an',cmd)
  self.assertIn('pad=1280:720',cmd[cmd.index('-vf')+1])
  self.assertIn('libx264',cmd)
 def test_source_offset_bounded(self):
  self.assertEqual(source_offset(103,8,6),1.5)
  self.assertEqual(source_offset(0,8,6),0)
 def test_concat_copies(self):
  self.assertIn('copy',concat_command('ffmpeg','concat.txt','final.mp4'))
if __name__=='__main__':unittest.main()
