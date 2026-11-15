import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from mv_local_preflight import inspect_source
from mv_repeatable_pipeline import file_sha
class LocalNoDropboxTests(unittest.TestCase):
 def test_hashes_and_length_without_render(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);im=root/"jacket.jpg";mp=root/"song.mp3"
   im.write_bytes(b"image test");mp.write_bytes(b"audio test")
   recipe={"version":1,"engine":"drawing-v42","song_id":"test",
           "duration_seconds":199.872,
           "expected_image_sha256":file_sha(im),
           "expected_audio_sha256":file_sha(mp),
           "renderer_sources":["mv_local_preflight.py"]}
   rp=root/"recipe.json";rp.write_text(json.dumps(recipe))
   fake=json.dumps({"format":{"duration":"199.840"},"streams":[{"codec_type":"audio","codec_name":"mp3"}]})
   from subprocess import CompletedProcess
   with patch("mv_local_preflight.subprocess.run",return_value=CompletedProcess([],0,fake,"")):
    result=inspect_source(rp,im,mp,root/"report.json")
   self.assertTrue(result["can_build_locally"])
   self.assertFalse(result["movie_generated"])
   self.assertFalse(result["dropbox_required"])
 def test_wrong_image_hash_fail_closed(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);im=root/"x";mp=root/"y";im.write_bytes(b"x");mp.write_bytes(b"y")
   recipe={"version":1,"engine":"drawing-v42","song_id":"test","duration_seconds":199.872,
           "expected_image_sha256":"0"*64,"expected_audio_sha256":file_sha(mp),
           "renderer_sources":["mv_local_preflight.py"]}
   rp=root/"recipe.json";rp.write_text(json.dumps(recipe))
   with self.assertRaises(ValueError):inspect_source(rp,im,mp)
if __name__=="__main__":unittest.main()
