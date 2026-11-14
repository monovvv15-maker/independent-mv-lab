"""Visual S16 pause-candidate inspection from V35 motion-only flags.
Private temporary footage and four small stills; never produces MV.
"""
import json,subprocess
from pathlib import Path
from v18_pexels_review import get_video
from v28_full_renderer import ffmpeg_bin
def main():
 root=Path("v35_pause_review");root.mkdir(exist_ok=True)
 video=root/"source.mp4"
 get_video({"page":"https://www.pexels.com/video/person-walking-on-concrete-floor-4464905/",
            "download":"https://www.pexels.com/download/video/4464905/"},video)
 ffmpeg=ffmpeg_bin()
 shots=[]
 try:
  for sec in [4.5,5.5,6.5,7.5,8.5]:
   out=root/(f"frame_{str(sec).replace('.','_')}.jpg")
   subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-y","-ss",str(sec),"-i",str(video),
       "-frames:v","1","-vf","scale=640:-2",str(out)],check=True,timeout=30)
   shots.append({"second":sec,"path":str(out)})
 finally:video.unlink(missing_ok=True)
 (root/"report.json").write_text(json.dumps({"id":4464905,"purpose":"check whether feet genuinely stop",
    "source":"real footage","still_review":"required","physical_stop_verified":False,"frames":shots},indent=2))
if __name__=="__main__":main()
