import unittest
from v17_neighborhood_gate import check
class V17Tests(unittest.TestCase):
 def test_not_same_as_visual_approval(self):
  item={"id":"a","width":1920,"height":1080,"duration_sec":8,"fps":30,"license_page":"Pexels Free","visual_status":"not_reviewed"}
  row=check([item])[0]
  self.assertTrue(row["metadata_compatible"])
  self.assertFalse(row["render_approved"])
 def test_portrait_rejected(self):
  item={"id":"a","width":1080,"height":1920,"duration_sec":8,"fps":30,"license_page":"Pexels Free","visual_status":"approved"}
  self.assertFalse(check([item])[0]["metadata_compatible"])
if __name__=="__main__": unittest.main()
