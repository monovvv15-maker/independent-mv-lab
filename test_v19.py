import unittest
from v19_timeline import draft
class Tests(unittest.TestCase):
 def test_not_ready_without_voice(self):self.assertFalse(draft()["render_ready"])
 def test_no_fake_boundaries(self):self.assertIsNone(draft()["cues"][1]["start"])
 def test_actual_vocal_value_moves_intro(self):self.assertEqual(draft(14.2)["cues"][0]["end"],14.2)
 def test_reject_invalid(self):
  with self.assertRaises(ValueError):draft(50)
if __name__=="__main__":unittest.main()
