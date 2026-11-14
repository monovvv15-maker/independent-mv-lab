import unittest
from v28_full_private_mux import cmd,DURATION
from v28_full_renderer import trim_command,source_offset
class V28MuxTests(unittest.TestCase):
 def test_full_song_not_30(self):
  c=cmd('ffmpeg','silent.mp4','song.mp3','out.mp4')
  self.assertIn(str(DURATION),c)
  self.assertNotIn('30',c)
 def test_no_network(self):self.assertNotIn('http',' '.join(cmd('ffmpeg','s','a','o')))
 def test_shot_output_no_audio(self):
  self.assertIn('-an',trim_command('ffmpeg','src','out',0,6))
 def test_offset(self):
  self.assertLessEqual(source_offset(6,15,8),6.5)
if __name__=='__main__':unittest.main()
