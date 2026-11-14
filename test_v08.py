import unittest
from v08_mixkit import classify,fetch_page,audit
class MixkitV08Tests(unittest.TestCase):
 def test_free(self):
  self.assertEqual(classify("Free Download Download this free stock video clip for commercial or personal use, under the Mixkit Stock Video Free License."),"verified_free")
 def test_restricted(self):
  self.assertEqual(classify("Free Download - 720p Version for Personal Use only. under the Mixkit Restricted License"),"restricted")
 def test_unknown(self):
  self.assertEqual(classify("Download now"),"unverified")
 def test_restricted_overrides_free(self):
  self.assertEqual(classify("under the Mixkit Stock Video Free License for commercial or personal use; under the Mixkit Restricted License"),"restricted")
 def test_unsafe_domain(self):
  with self.assertRaises(ValueError):fetch_page("https://not-mixkit.co/free-stock-video/x/")
 def test_requires_live_verification(self):
  rows=[{"url":"https://mixkit.co/free-stock-video/example-123/","expected_license":"free","scene":"01_morning"}]
  self.assertFalse(audit(rows,lambda _: "no license information")[0]["eligible"])
 def test_negative_control(self):
  rows=[{"url":"https://mixkit.co/free-stock-video/example-123/","expected_license":"restricted","scene":"01_morning"}]
  self.assertFalse(audit(rows,lambda _: "for commercial or personal use under the Mixkit Stock Video Free License")[0]["eligible"])
if __name__=="__main__":unittest.main()
