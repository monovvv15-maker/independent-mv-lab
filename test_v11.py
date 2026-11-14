import unittest
from v11_clip_previews import find_preview_urls
class TestV11(unittest.TestCase):
 def test_explicit_only(self):
  urls=find_preview_urls('<video src="https://static.mixkit.co/videos/a.mp4"></video>',"https://mixkit.co/x/")
  self.assertEqual(urls,["https://static.mixkit.co/videos/a.mp4"])
 def test_no_guess(self):
  self.assertEqual(find_preview_urls("video name and ID 123 only","https://mixkit.co/free-stock-video/a-123/"),[])
 def test_untrusted_rejected(self):
  self.assertEqual(find_preview_urls('<video src="https://bad.example.org/a.mp4">',"https://mixkit.co/"),[])
if __name__=="__main__":unittest.main()
