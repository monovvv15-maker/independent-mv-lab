import copy,json,unittest
from v35_director_audit import audit,PATH
class V35Tests(unittest.TestCase):
 def setUp(self):self.data=json.loads(PATH.read_text(encoding="utf-8"))
 def test_no_karaoke_ready(self):self.assertFalse(audit(self.data)["render_ready"])
 def test_all_have_unique_id(self):self.assertEqual(audit(self.data)["failures"],[])
 def test_reuse_fails(self):
  d=copy.deepcopy(self.data);d["shots"][5]["source_id"]=d["shots"][0]["source_id"]
  self.assertTrue(any("repeat" in e for e in audit(d)["failures"]))
 def test_invented_time_fails(self):
  d=copy.deepcopy(self.data);d["shots"][0]["time_start"]=1.0
  self.assertTrue(audit(d)["failures"])
 def test_one_footwear_person_in_opening(self):self.assertEqual(self.data["shots"][0]["source_id"],"4953053")
 def test_new_bloom(self):self.assertEqual(self.data["shots"][19]["source_id"],"27571663")
 def test_false_stop_rejected(self):
  d=copy.deepcopy(self.data)
  for shot in d["shots"]:
   if shot["shot_id"]=="S16":
    shot["source_id"]="4464905"
    shot["source_status"]="real_three_frame_review_candidate"
  self.assertTrue(any("false foot stop" in x for x in audit(d)["failures"]))
if __name__=="__main__":unittest.main()
