import unittest
from v26_editorial_planner import score,propose,inspect
class V26Tests(unittest.TestCase):
 def test_repeat_penalty(self):
  c={"id":1,"license_page":"Free","duration":12,"width":1920,"height":1080,"fps":30,"tags":["morning"]}
  self.assertGreater(score(c,{"morning":3},None,{}),score(c,{"morning":3},1,{1:2}))
 def test_restricted_excluded(self):
  c={"id":1,"license_page":"Restricted","duration":12,"tags":["rain"]}
  self.assertLess(score(c,{"rain":3},None,{}),0)
 def test_no_false_approval(self):
  c={"id":1,"url":"https://example.com","license_page":"Free","duration":12,"tags":["rain","morning","city","people","memory","train","stillness","flower","ending","sunset"]}
  plan=propose([c])
  self.assertTrue(all(x["ready_for_render"] is False for x in plan))
  self.assertEqual(inspect(plan),[])
 def test_implicit_chapters(self):
  from v26_editorial_planner import CHAPTERS
  self.assertEqual(CHAPTERS[0][0],0)
  self.assertEqual(CHAPTERS[-1][1],199.872)
if __name__=="__main__":unittest.main()
