import json,unittest
from pathlib import Path
from v34_editorial_gate import evaluate,PLAN
class Tests(unittest.TestCase):
 def setUp(self):self.data=json.loads(PLAN.read_text(encoding='utf-8'))
 def test_grounded_candidates(self):self.assertEqual(evaluate(self.data)['evaluated_sources'],8)
 def test_no_auto_render(self):self.assertFalse(evaluate(self.data)['render_ready'])
 def test_evidence_accepted(self):self.assertEqual(evaluate(self.data)['errors'],[])
 def test_reject_cannot_enter_edit(self):
  d=json.loads(json.dumps(self.data));d['source_evidence']['6136988']['approved_for_edit']=True
  self.assertTrue(evaluate(d)['errors'])
 def test_timing_not_invented(self):
  d=json.loads(json.dumps(self.data));d['timing']='verified'
  self.assertTrue(evaluate(d)['errors'])
if __name__=="__main__":unittest.main()
