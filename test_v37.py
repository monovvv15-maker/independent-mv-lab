import unittest
from v37_unique_renderer import validate,assign
class V37QA(unittest.TestCase):
 def setUp(self):
  self.shots=[{"id":i,"weight":8,"grammar":str(i)} for i in range(1,26)]
  self.shots[0]["id"]=4953053
 def test_all_distinct(self):self.assertTrue(validate(self.shots))
 def test_repeated_clip_rejected(self):
  self.shots[4]["id"]=self.shots[3]["id"]
  with self.assertRaises(ValueError):validate(self.shots)
 def test_duration_allocation(self):
  real={s["id"]:11. for s in self.shots}
  d=assign(self.shots,real)
  self.assertAlmostEqual(sum(d),199.872,places=3)
  self.assertEqual(len(d),25)
 def test_insufficient_real_footage_rejected(self):
  with self.assertRaises(ValueError):assign(self.shots,{s["id"]:5 for s in self.shots})
 def test_rejected_footage_blocked(self):
  self.shots[3]["id"]=5034328
  with self.assertRaises(ValueError):validate(self.shots)
if __name__=="__main__":unittest.main()
