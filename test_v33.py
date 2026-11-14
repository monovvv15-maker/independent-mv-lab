import json,unittest
from pathlib import Path
from v33_director_gate import validate,status,PLAN
class V33Tests(unittest.TestCase):
 def setUp(self):self.data=json.loads(PLAN.read_text(encoding="utf-8"))
 def test_story_semantics(self):self.assertEqual(validate(self.data),[])
 def test_no_generated_media(self):self.assertFalse(status(self.data)["video_generated"])
 def test_missing_shots_block(self):self.assertFalse(status(self.data)["ready_to_render"])
 def test_repeated_source_fails(self):
  d=json.loads(json.dumps(self.data))
  d["shots"][1]["source_id"]=d["shots"][0]["source_id"]
  self.assertTrue(any("reused source" in e for e in validate(d)))
 def test_character_progression(self):
  roles={s["role"] for s in self.data["shots"]}
  self.assertTrue({"action","comparison","pause","discovery","future"}.issubset(roles))
 def test_no_fake_timing(self):self.assertTrue(all(s["time_start"] is None for s in self.data["shots"]))
if __name__=="__main__":unittest.main()
