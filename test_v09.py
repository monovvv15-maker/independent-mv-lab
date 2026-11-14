import unittest
from v09_storyboard import CUES, plan, assess
class V09Test(unittest.TestCase):
 def test_six_cues_cover_30s(self):
  self.assertEqual(len(CUES),6)
  self.assertEqual([(x["start"],x["end"]) for x in CUES],[(i,i+5) for i in range(0,30,5)])
 def test_restricted_not_used(self):
  row={"id":"a","scene":"02_rain","eligible":False,"duration":10,"fps":30,"url":"https://example.org","title":"rain"}
  self.assertIsNone(assess(row,CUES[1]))
 def test_sunset_penalty(self):
  base={"id":"a","scene":"03_door","eligible":True,"duration":8,"fps":30,"url":"https://example.org","title":"shoes"}
  self.assertGreater(assess({**base,"note":"morning"},CUES[2])["score"],assess({**base,"note":"sunset"},CUES[2])["score"])
 def test_does_not_claim_visual_approval(self):
  row={"id":"a","scene":"01_morning","eligible":True,"duration":8,"fps":30,"url":"https://example.org","title":"street"}
  result=plan([row])
  self.assertEqual(result[0]["status"],"UNVERIFIED_VISUAL")
  self.assertEqual(result[0]["timing_status"],"PROVISIONAL")
  self.assertIsNone(result[1]["recommendation"])
if __name__=="__main__":unittest.main()
