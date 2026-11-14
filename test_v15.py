import unittest
from v15_candidates import evaluate_candidate
class V15CandidateTests(unittest.TestCase):
 def test_portrait_not_preferred(self):
  self.assertFalse(evaluate_candidate({"id":"x","scene":"shoes","width":1080,"height":1920,"fps":30,"duration":9})["geometry_preference"])
 def test_film_2398_accepted_for_geometry(self):
  self.assertTrue(evaluate_candidate({"id":"x","scene":"shoes","width":3840,"height":2160,"fps":23.98,"duration":9})["geometry_preference"])
 def test_never_auto_visual_approve(self):
  self.assertFalse(evaluate_candidate({"id":"x","scene":"shoes","width":3840,"height":2160,"fps":24,"duration":9})["render_approved"])
if __name__=="__main__":unittest.main()
