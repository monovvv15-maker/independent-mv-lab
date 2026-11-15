"""No-media simulated end-to-end test of V1 resumable workflow.

All fake outputs are byte strings, not playable pictures or video.
Tests a failure at mux then reusing both preflight and render.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mv_repeatable_pipeline import execute,file_sha

class EndToEndResumeTest(unittest.TestCase):
 def test_resume_after_mux_failure_without_re_rendering(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   jacket=root/"jacket.bin"
   audio=root/"song.bin"
   jacket.write_bytes(b"private sample jacket bytes")
   audio.write_bytes(b"private sample audio bytes")
   recipe={
    "version":1,"engine":"drawing-v42","song_id":"simulation-only",
    "expected_image_sha256":file_sha(jacket),
    "expected_audio_sha256":file_sha(audio),
    "renderer_sources":["mv_repeatable_pipeline.py"],
    "duration_seconds":199.872,"mobile_size":540
   }
   rp=root/"recipe.json";rp.write_text(json.dumps(recipe),encoding="utf-8")
   work=root/"work"
   renders=[]
   mux_calls=[]
   def render_stub(r,i,w,out):
    renders.append(1)
    Path(out).write_bytes(b"fake silent pixels")
    return out
   def mux_stub(v,a,out,seconds):
    mux_calls.append(1)
    if len(mux_calls)==1:raise RuntimeError("simulation: mux failed")
    Path(out).write_bytes(b"fake audio-bearing bytes")
    return out
   def mobile_stub(m,out,size):
    Path(out).write_bytes(b"fake mobile bytes")
    return out
   def verify_stub(path,seconds,must_audio):
    return {"duration":seconds,"size":Path(path).stat().st_size,
            "streams":[{"codec_type":"video","codec_name":"h264"}]+(
            [{"codec_type":"audio","codec_name":"aac"}] if must_audio else [])}
   with patch("mv_repeatable_pipeline.render_silent",side_effect=render_stub),\
        patch("mv_repeatable_pipeline.mux_audio",side_effect=mux_stub),\
        patch("mv_repeatable_pipeline.make_mobile",side_effect=mobile_stub),\
        patch("mv_repeatable_pipeline.verify_movie",side_effect=verify_stub):
    with self.assertRaisesRegex(RuntimeError,"mux failed"):
     execute(rp,work,jacket,audio,authorize_render=True)
    failed=json.loads((work/"last_run.json").read_text())
    self.assertEqual(failed["failed"],"mux")
    self.assertEqual(failed["completed"],["preflight","render"])
    recovered=execute(rp,work,jacket,audio,authorize_render=True)
    self.assertEqual(recovered["reused"],["preflight","render"])
    self.assertEqual(recovered["completed"],["mux","verify","package"])
    self.assertEqual(len(renders),1)
    self.assertEqual(len(mux_calls),2)
    final=execute(rp,work,jacket,audio,authorize_render=True)
    self.assertEqual(final["reused"],["preflight","render","mux","verify","package"])
    self.assertEqual(len(renders),1)
    self.assertEqual(len(mux_calls),2)
if __name__=="__main__":unittest.main()
