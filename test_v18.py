import unittest
from v18_pexels_review import valid_final_url
class TestV18(unittest.TestCase):
 def test_cdnhost(self):self.assertTrue(valid_final_url("https://videos.pexels.com/video-files/a/b.mp4"))
 def test_no_subdomain_confusion(self):self.assertFalse(valid_final_url("https://videos.pexels.com.evil.test/a.mp4"))
 def test_no_http(self):self.assertFalse(valid_final_url("http://videos.pexels.com/a.mp4"))
 def test_no_random_host(self):self.assertFalse(valid_final_url("https://example.com/a.mp4"))
if __name__=="__main__":unittest.main()
