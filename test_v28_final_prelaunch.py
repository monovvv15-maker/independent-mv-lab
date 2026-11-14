import unittest
from v28_final_prelaunch import run
class Tests(unittest.TestCase):
 def test_fails_if_not_downloaded(self):
  item={'id':1,'duration':12,'license_page':'Free','tags':['morning','rain','street','walking','city','people','crossing','memory','old_town','train','stillness','flower','wind','ending','sunset'],'url':'https://www.pexels.com/video/example-1/'}
  self.assertFalse(run([item])['technical_preflight_pass'])
 def test_can_pass_technical_but_not_quality(self):
  item={'id':1,'duration':12,'license_page':'Free','retrieval_status':'preview_frame_extracted','tags':['morning','rain','street','walking','city','people','crossing','memory','old_town','train','stillness','flower','wind','ending','sunset'],'url':'https://www.pexels.com/video/example-1/'}
  r=run([item])
  self.assertTrue(r['technical_preflight_pass'])
  self.assertFalse(r['quality_approved'])
  self.assertFalse(r['render_executed'])
if __name__=='__main__':unittest.main()
