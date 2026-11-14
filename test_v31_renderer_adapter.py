import unittest
from v31_renderer_adapter import graded_trim_command,validate_command
class V31AdapterTests(unittest.TestCase):
 def test_jacket_grading_wired(self):
  c=graded_trim_command('ffmpeg','src','dst',0,5)
  self.assertTrue(validate_command(c))
 def test_no_audio_overlay(self):
  c=graded_trim_command('ffmpeg','src','dst',0,5)
  self.assertIn('-an',c)
 def test_no_generated_media(self):
  c=graded_trim_command('ffmpeg','src','dst',0,5)
  self.assertEqual(c[-1],'dst')
if __name__=="__main__":unittest.main()
