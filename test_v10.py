import unittest
from v10_preflight import evaluate
class V10Preflight(unittest.TestCase):
 def test_fail_closed(self):
  rows=[{"start":0,"end":5,"scene":"morning","recommendation":{"title":"Dawn","issues":[],"visual_review":"pending"},"timing_status":"PROVISIONAL"}]
  self.assertFalse(evaluate(rows)["render_ready"])
 def test_sunset_rejected(self):
  rows=[{"start":0,"end":5,"scene":"shoes","recommendation":{"title":"Sunset","issues":["sunset conflicts with morning"],"visual_review":"approved"},"timing_status":"VERIFIED"}]
  self.assertFalse(evaluate(rows)["render_ready"])
 def test_verified_ready(self):
  rows=[{"start":0,"end":5,"scene":"rain","recommendation":{"title":"Puddle","issues":[],"visual_review":"approved"},"timing_status":"VERIFIED"}]
  self.assertTrue(evaluate(rows)["render_ready"])
if __name__=="__main__":unittest.main()
