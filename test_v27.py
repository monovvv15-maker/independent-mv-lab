import unittest
from v27_music_cut_planner import CUT_ENDS,plan,validate
class V27Tests(unittest.TestCase):
 def test_34_beats(self):self.assertEqual(len(CUT_ENDS),34)
 def test_full_duration(self):self.assertEqual(CUT_ENDS[-1],199.872)
 def test_source_candidate_not_approved(self):
  c={'id':1,'url':'https://pexels.com/example','duration':12,'tags':['morning','rain','street','walking','people','city','old_town','train','stillness','wind','flower','ending','sunset'],'license_page':'Free'}
  shots=plan([c])
  self.assertEqual(validate(shots),[])
  self.assertTrue(all(not s['render_authorized'] for s in shots))
 def test_non_licensed_fails(self):
  c={'id':1,'duration':12,'tags':['morning'],'license_page':'Restricted'}
  with self.assertRaises(ValueError):plan([c])
if __name__=='__main__':unittest.main()
