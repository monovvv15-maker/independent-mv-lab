"""Local/no-Dropbox MV preflight for the conversation workspace.

Reads existing creator-provided originals, verifies hashes, and emits only
non-sensitive QA metadata in an isolated workspace. No image or video output.
When authorized, use the existing mv_repeatable_pipeline.py with these
same verified files, independently of GitHub Actions secrets.
"""
import argparse
import json
import subprocess
from pathlib import Path
from mv_repeatable_pipeline import check_private_assets,load_recipe,atomic_json

def inspect_source(recipe_path,image_path,audio_path,output=None):
    recipe=load_recipe(recipe_path)
    check_private_assets(recipe,image_path,audio_path)
    command=["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name",
             "-of","json",str(audio_path)]
    r=subprocess.run(command,capture_output=True,text=True,check=True)
    audio=json.loads(r.stdout)
    duration=float(audio["format"]["duration"])
    expected=float(recipe["duration_seconds"])
    if abs(duration-expected)>1:
        raise ValueError("Original MP3 duration differs from production recipe")
    if not any(s.get("codec_type")=="audio" for s in audio.get("streams",[])):
        raise ValueError("Audio stream missing")
    # No private paths emitted in report.
    result={"source_verified":True,"jacket_sha_matches":True,"audio_sha_matches":True,
      "audio_duration_seconds":round(duration,3),"timeline_seconds":expected,
      "can_build_locally":True,"github_secrets_required":False,"dropbox_required":False,
      "movie_generated":False,"lyric_cues_verified":False}
    if output is not None:atomic_json(output,result)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--recipe",default="catalog/mv_repeatable_recipe_v1.json")
    p.add_argument("--image",required=True)
    p.add_argument("--audio",required=True)
    p.add_argument("--report",default=".mv-build/local_preflight.json")
    args=p.parse_args()
    print(json.dumps(inspect_source(args.recipe,args.image,args.audio,args.report),
      ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
