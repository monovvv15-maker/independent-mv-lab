import json,copy,unittest
from v36_no_repeat_qa import P,validate
class TestV36(unittest.TestCase):
 def setUp(self):self.d=json.loads(P.read_text(encoding="utf-8"))
 def test_valid(self):self.assertEqual(validate(self.d),[])
 def test_no_video(self):self.assertFalse(self.d["video_generated"])
 def test_source_reuse_fails(self):
  d=copy.deepcopy(self.d);d["scenes"][1]["source"][0]=d["scenes"][0]["source"][0]
  self.assertTrue(validate(d))
 def test_same_grammar_fails(self):
  d=copy.deepcopy(self.d);d["scenes"][1]["grammar"]=d["scenes"][0]["grammar"]
  self.assertTrue(validate(d))
 def test_unresolved_stops_preserved(self):self.assertTrue(any("foot stops" in x for x in self.d["unresolved_actions"]))
if __name__=="__main__":unittest.main()
