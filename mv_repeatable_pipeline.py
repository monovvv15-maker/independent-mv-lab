"""Reusable MV production pipeline with resumable, content-addressed stage receipts.

Never stores original private media in git. A stage is reused only when its
inputs, code/config and verified outputs have matching digests.
New MV rendering requires --authorize-render and an explicit workflow dispatch.
Standard library only; source renderers run as subprocesses.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STAGES=("preflight","render","mux","verify","package")
SCRIPT_VERSION="mv-repeatable-v1-20261115"
def file_sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=path.parent,delete=False) as f:
        json.dump(obj,f,ensure_ascii=False,indent=2,sort_keys=True)
        tmp=f.name
    os.replace(tmp,path)

def load_recipe(recipe_path):
    data=json.loads(Path(recipe_path).read_text(encoding="utf8"))
    if data.get("version")!=1 or data.get("engine")!="drawing-v42":
        raise ValueError("Unsupported recipe")
    for k in ("song_id","expected_image_sha256","expected_audio_sha256","renderer_sources"):
        if not data.get(k):raise ValueError("Recipe missing "+k)
    if data.get("duration_seconds",0)<=0:raise ValueError("invalid duration")
    if not data.get("expected_image_sha256") or not data.get("expected_audio_sha256"):
        raise ValueError("must pin private source digests")
    return data

def check_private_assets(recipe,image,audio):
    for path,expected,label in ((image,recipe["expected_image_sha256"],"jacket"),
                                (audio,recipe["expected_audio_sha256"],"audio")):
        if not path or not Path(path).is_file():
            raise FileNotFoundError(f"Missing private {label}; never replace with a public or dummy asset")
        actual=file_sha(path)
        if actual.lower()!=expected.lower():
            raise ValueError(f"private {label} SHA256 mismatch")
    return True

def stage_key(stage,recipe,prior=None,source_hashes=None):
    return digest({"version":SCRIPT_VERSION,"stage":stage,"recipe":recipe,
                   "prior":prior or [],"source_hashes":source_hashes or {}})

def receipt_path(work,stage):
    return Path(work)/"receipts"/(stage+".json")

def cache_valid(work,stage,key):
    p=receipt_path(work,stage)
    if not p.is_file():return False
    try:
        r=json.loads(p.read_text(encoding="utf8"))
        if r.get("key")!=key or r.get("state")!="complete":return False
        files=r.get("outputs",{})
        if not files:return False
        root=Path(work).resolve()
        for relative,expected in files.items():
            out=(root/relative).resolve()
            if not out.is_relative_to(root) or not out.is_file() or file_sha(out)!=expected:
                return False
        return True
    except (OSError,ValueError,TypeError,KeyError):
        return False

def record(work,stage,key,outputs):
    root=Path(work).resolve()
    result={}
    for file in outputs:
        path=Path(file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("output outside isolated workspace")
        if not path.is_file() or path.stat().st_size==0:
            raise ValueError("missing/empty output: "+str(path))
        result[str(path.relative_to(root))]=file_sha(path)
    atomic_json(receipt_path(work,stage),{"key":key,"state":"complete","outputs":result,
             "pipeline_version":SCRIPT_VERSION,"stage":stage})
    return result

def run_command(cmd,log_path=None):
    result=subprocess.run(cmd,capture_output=True,text=True,check=False)
    if log_path:
        Path(log_path).parent.mkdir(parents=True,exist_ok=True)
        Path(log_path).write_text(result.stdout+"\n"+result.stderr,encoding="utf8")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {cmd[0]}: {result.stderr[-350:]}")
    return result

def probe(path):
    cmd=["ffprobe","-v","error","-show_entries",
         "format=duration,size:stream=codec_type,codec_name,width,height",
         "-of","json",str(path)]
    return json.loads(run_command(cmd).stdout)

def verify_movie(movie,expected_duration,must_audio):
    p=probe(movie)
    duration=float(p["format"]["duration"])
    if not abs(duration-float(expected_duration))<=0.4:
        raise ValueError(f"duration mismatch: {duration} vs {expected_duration}")
    streams=p["streams"]
    if not any(x.get("codec_type")=="video" and x.get("codec_name")=="h264" for x in streams):
        raise ValueError("H.264 video missing")
    if must_audio and not any(x.get("codec_type")=="audio" and x.get("codec_name")=="aac" for x in streams):
        raise ValueError("AAC audio missing")
    if not must_audio and any(x.get("codec_type")=="audio" for x in streams):
        raise ValueError("Silent master unexpectedly contains audio")
    return {"duration":duration,"size":int(p["format"]["size"]),"streams":streams}

def render_silent(recipe,image,work,output):
    # Renderer reads private image locally only. It never uploads it.
    cmd=[sys.executable,"mv_drawing_render.py","--image",str(image),
         "--out",str(output),"--fps",str(recipe.get("fps",24)),
         "--size",str(recipe.get("master_size",720)),
         "--seconds",str(recipe["duration_seconds"])]
    run_command(cmd,Path(work)/"logs"/"render.log")
    return output

def mux_audio(video,audio,out,seconds):
    run_command(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
        "-i",str(video),"-i",str(audio),"-map","0:v:0","-map","1:a:0",
        "-c:v","copy","-c:a","aac","-b:a","160k","-t",str(seconds),
        "-movflags","+faststart",str(out)])
    return out

def make_mobile(master,out,size=540):
    run_command(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
        "-i",str(master),"-vf",f"scale={size}:{size}","-c:v","libx264",
        "-preset","veryfast","-crf","26","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","96k","-movflags","+faststart",str(out)])
    return out

def execute(recipe_path,work_dir,image=None,audio=None,authorize_render=False,dry_run=False):
    recipe=load_recipe(recipe_path)
    work=Path(work_dir).resolve()
    work.mkdir(parents=True,exist_ok=True)
    if dry_run:
        # Dry-run never executes render, even with apparent approval.
        return {"dry_run":True,"ready":bool(image and audio and Path(image).is_file() and Path(audio).is_file()),
                "stages":list(STAGES),"video_generated":False}
    if not authorize_render:
        raise PermissionError("Video generation explicitly requires --authorize-render")
    check_private_assets(recipe,image,audio)
    # Hash all renderer/code and scene inputs to invalidate cache when editing changes.
    sources={}
    for name in recipe["renderer_sources"]:
        p=Path(name)
        if not p.is_file():raise FileNotFoundError("Renderer dependency absent: "+name)
        sources[name]=file_sha(p)
    source_digests={"jacket":file_sha(image),"audio":file_sha(audio),**sources}
    products=work/"products";products.mkdir(exist_ok=True)
    state={"song_id":recipe["song_id"],"completed":[],"reused":[],"failed":None}
    previous=[]
    try:
        for stage in STAGES:
            key=stage_key(stage,recipe,previous,source_digests)
            if cache_valid(work,stage,key):
                state["reused"].append(stage)
                previous.append(key);continue
            # Each stage writes only into work_dir. Failed stages have no complete receipt.
            out=products
            if stage=="preflight":
                payload={"asset_digests":{"jacket":source_digests["jacket"],"audio":source_digests["audio"]},
                         "recipe_sha":file_sha(recipe_path),"duration_seconds":recipe["duration_seconds"]}
                p=work/"preflight.json";atomic_json(p,payload);outputs=[p]
            elif stage=="render":
                p=out/"master_silent.mp4"
                render_silent(recipe,image,work,p)
                verify_movie(p,recipe["duration_seconds"],must_audio=False)
                outputs=[p]
            elif stage=="mux":
                p=out/"master_audio.mp4"
                mux_audio(out/"master_silent.mp4",audio,p,recipe["duration_seconds"])
                verify_movie(p,recipe["duration_seconds"],must_audio=True)
                outputs=[p]
            elif stage=="verify":
                p=work/"qa.json"
                payload={"master":verify_movie(out/"master_audio.mp4",recipe["duration_seconds"],True),
                         "silent":verify_movie(out/"master_silent.mp4",recipe["duration_seconds"],False),
                         "lyric_alignment":"unverified","editorial_quality":"human_review_required"}
                atomic_json(p,payload);outputs=[p]
            elif stage=="package":
                mobile=out/"iphone.mp4"
                make_mobile(out/"master_audio.mp4",mobile,int(recipe.get("mobile_size",540)))
                verify_movie(mobile,recipe["duration_seconds"],True)
                delivery=work/"delivery.json"
                atomic_json(delivery,{"files":["products/master_audio.mp4","products/iphone.mp4"],
                         "qa":"qa.json","source_sha":source_digests,"status":"rendered_not_editorially_approved"})
                outputs=[mobile,delivery]
            record(work,stage,key,outputs)
            state["completed"].append(stage)
            previous.append(key)
    except Exception as e:
        state["failed"]=stage
        state["error"]=str(e)
        atomic_json(work/"last_run.json",state)
        raise
    atomic_json(work/"last_run.json",state)
    return state

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--recipe",default="catalog/mv_repeatable_recipe_v1.json")
    p.add_argument("--workspace",default=".mv-build")
    p.add_argument("--image")
    p.add_argument("--audio")
    p.add_argument("--authorize-render",action="store_true")
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args()
    result=execute(a.recipe,a.workspace,a.image,a.audio,a.authorize_render,a.dry_run)
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
