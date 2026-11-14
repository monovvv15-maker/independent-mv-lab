import unittest
from v25_full_length import CHAPTERS,DURATION,validate,status
class V25Tests(unittest.TestCase):
 def test_duration(self):self.assertEqual(CHAPTERS[-1]["end"],DURATION)
 def test_no_gaps(self):self.assertEqual(validate(),[])
 def test_no_fake_lyrics(self):self.assertTrue(all(c["lyric_alignment"]=="unverified" for c in CHAPTERS))
 def test_not_ready(self):self.assertFalse(status()["render_ready"])
 def test_six_chapters(self):self.assertEqual(len(CHAPTERS),6)
if __name__=="__main__":unittest.main()
