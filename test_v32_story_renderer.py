import unittest
from v32_story_renderer import story_check,CHAPTERS,ids,SONG_LENGTH
class Tests(unittest.TestCase):
 def test_canonical_chapters(self):self.assertEqual(len(CHAPTERS),7)
 def test_first_frame_shoes(self):self.assertEqual(CHAPTERS[0][2][0][0],4953053)
 def test_total_time(self):self.assertAlmostEqual(sum(c[1] for c in CHAPTERS),SONG_LENGTH,places=3)
 def test_no_fake_stories(self):self.assertEqual(story_check(),[])
 def test_selected_source_count(self):self.assertGreaterEqual(len(ids),15)
if __name__=="__main__":unittest.main()
