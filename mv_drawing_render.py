"""Render a V42 drawing film from private local image into a silent master.

Only invoked by explicitly authorized repeatable pipeline. No media is uploaded
to repository. Retains V40 one-time correction and final source title.
"""
import argparse
import json
import subprocess
from pathlib import Path
from v39_progressive_drawing import validated_image,base_without_title,derive_pencil,make_draw_map,DURATION
from v42_timing_bridge import cue_manifest,preflight,draw_at

def generate_frames(image,seconds,fps=24,size=720):
    if size!=720:
        raise ValueError("V42 source fidelity is QA-calibrated for 720 square")
    cue=cue_manifest()
    if not preflight(cue)["pass"]:
        raise RuntimeError("cue manifest failed QA")
    original=validated_image(image,strict=True)
    clean=base_without_title(original)
    pencil=derive_pencil(original)
    order=make_draw_map(original.shape)
    count=round(seconds*fps)
    # Last generated frame is before total length; avoid end-boundary overflow.
    for idx in range(count):
        t=min(idx/fps,DURATION)
        yield draw_at(t,original,cue,clean=clean,pencil=pencil,order=order)

def run(image,out,fps,size,seconds):
    if abs(seconds-DURATION)>.01:
        raise ValueError("Recipe duration must match V42 drawing duration")
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
         "-f","rawvideo","-pix_fmt","bgr24","-s",f"{size}x{size}",
         "-r",str(fps),"-i","-","-an","-c:v","libx264",
         "-preset","veryfast","-crf","23","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(dest)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for frame in generate_frames(image,seconds,fps,size):
            process.stdin.write(frame.tobytes())
    except Exception:
        process.kill()
        process.wait()
        dest.unlink(missing_ok=True)
        raise
    finally:
        if process.stdin and not process.stdin.closed:
            process.stdin.close()
    if process.wait()!=0 or not dest.exists() or dest.stat().st_size==0:
        raise RuntimeError("Video encoding failed")
    print(json.dumps({"output":str(dest),"seconds":seconds,"fps":fps,"private_original_preserved":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--image",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--seconds",type=float,required=True)
    p.add_argument("--fps",type=int,default=24)
    p.add_argument("--size",type=int,default=720)
    a=p.parse_args()
    run(a.image,a.out,a.fps,a.size,a.seconds)
