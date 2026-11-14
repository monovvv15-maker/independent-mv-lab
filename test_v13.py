import unittest
from v13_edl import check_edl,make_draft
class TestV13(unittest.TestCase):
 def test_draft_is_blocked(self):self.assertTrue(check_edl(make_draft()))
 def test_full_coverage(self):self.assertEqual((make_draft()[0]["start"],make_draft()[-1]["end"]),(0,30))
 def test_invalid_people_blocked(self):
  a={"start":0,"end":15,"license_verified":True,"visual_review":"approved","audio_sync":"verified","source_fps":30,"full_video_downloaded":True,"crop_approved":True,"protagonist":"A"}
  b={**a,"start":15,"end":30,"protagonist":"B"}
  self.assertIn("mixed protagonist identity",check_edl([a,b]))
 def test_verified_edl_accepted(self):
  a={"start":0,"end":30,"license_verified":True,"visual_review":"approved","audio_sync":"verified","source_fps":30,"full_video_downloaded":True,"crop_approved":True,"protagonist":"no_person"}
  self.assertEqual(check_edl([a]),[])
if __name__=="__main__":unittest.main()
