import io
import json
import tempfile
import unittest
from pathlib import Path
from media_sources import commons_search, commons_license
from review import build_review

class MockResponse(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

def mocked(payload):
    def opener(request, timeout=25):
        return MockResponse(json.dumps(payload).encode())
    return opener

class TestDiscovery(unittest.TestCase):
    def test_license_allow(self):
        self.assertTrue(commons_license({"LicenseShortName":{"value":"CC BY 4.0"}})[2])
    def test_license_block(self):
        self.assertFalse(commons_license({"LicenseShortName":{"value":"CC BY-NC-ND 4.0"}})[2])
    def test_license_unknown(self):
        self.assertFalse(commons_license({})[2])
    def test_commons_metadata(self):
        payload = {"query":{"pages":{"10":{"pageid":10,"title":"File:Sample.webm","imageinfo":[{"mime":"video/webm","url":"https://upload.wikimedia.org/sample.webm","descriptionurl":"https://commons.wikimedia.org/wiki/File:Sample.webm","extmetadata":{"LicenseShortName":{"value":"CC0"}}}]}}}}
        rows = commons_search("rain", opener=mocked(payload))
        self.assertEqual(rows[0]["id"], "commons_10")
        self.assertTrue(rows[0]["license_ok"])
    def test_non_video_removed(self):
        payload = {"query":{"pages":{"10":{"pageid":10,"title":"File:Sample.jpg","imageinfo":[{"mime":"image/jpeg","url":"https://upload.wikimedia.org/sample.jpg","descriptionurl":"https://commons.wikimedia.org/wiki/File:Sample.jpg","extmetadata":{"LicenseShortName":{"value":"CC0"}}}]}}}}
        self.assertEqual(commons_search("rain", opener=mocked(payload)), [])
    def test_review_escaping(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"index.html"
            build_review([{"license_ok": True,"title":"<script>","source_url":"https://commons.wikimedia.org/a","license":"CC0"}], output)
            text = output.read_text(encoding="utf-8")
            self.assertIn("&lt;script&gt;", text)
            self.assertNotIn("<script>", text)
if __name__=="__main__": unittest.main()
