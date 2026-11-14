import unittest,tempfile
from pathlib import Path
from v14_renderer import commands
class RendererTests(unittest.TestCase):
 def test_rejects_unapproved(self):
  with self.assertRaises(ValueError):
   commands([{"start":0,"end":30,"license_verified":False,"visual_review":"pending","audio_sync":"unverified","source_fps":30,"full_video_downloaded":False,"crop_approved":False} ],Path("song.mp3"),Path("out.mp4"))
 def test_requires_audio(self):
  with self.assertRaises(FileNotFoundError):
   commands([{"start":0,"end":30,"license_verified":True,"visual_review":"approved","audio_sync":"verified","source_fps":30,"full_video_downloaded":True,"crop_approved":True,"protagonist":"no_person","local_video":"footage.mp4"}],Path("song-does-not-exist.mp3"),Path("out.mp4"))
 def test_command_without_executing(self):
  with tempfile.TemporaryDirectory() as d:
   audio=Path(d)/"song.mp3";clip=Path(d)/"clip.mp4"
   audio.write_bytes(b"mock");clip.write_bytes(b"mock")
   item={"start":0,"end":30,"license_verified":True,"visual_review":"approved","audio_sync":"verified","source_fps":30,"full_video_downloaded":True,"crop_approved":True,"protagonist":"no_person","local_video":str(clip)}
   c=commands([item],audio,Path(d)/"out.mp4")
   self.assertIn("libx264",c)
   self.assertIn("concat=n=1",c[c.index("-filter_complex")+1])
if __name__=="__main__":unittest.main()
