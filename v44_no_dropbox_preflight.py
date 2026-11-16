"""V44 no-render local preflight before creator-approved video generation.

Inspect already-provided ORIGINALS, recipe and cue semantics. Does not
export frames or media, download files, or require Dropbox.
"""
from __future__ import annotations
import argparse, json, hashlib, subprocess, shutil, sys
from pathlib import Path
from mv_repeatable_pipeline import load_recipe,check_private_assets
from v39_progressive_drawing import DURATION,EXPECTED_SOURCE_SHA256,PHASES
from v41_redraw_engine import quality_gate
from v42_timing_bridge import cue_manifest,preflight as time_preflight

RENDERER_FILES=("mv_repeatable_pipeline.py","mv_drawing_render.py",
                "v39_progressive_drawing.py","v41_redraw_engine.py",
                "v42_timing_bridge.py","catalog/v42_audio_cue_manifest.json")
def check(source_image=None,source_audio=None,recipe_path="catalog/mv_repeatable_recipe_v1.json"):
    failures=[];warnings=[]
    recipe=load_recipe(recipe_path)
    if set(RENDERER_FILES)-set(recipe["renderer_sources"]):
        failures.append("renderer dependency is not SHA-pinned")
    for rel in recipe["renderer_sources"]:
        if not Path(rel).is_file():failures.append("missing dependency: "+rel)
    if recipe["expected_image_sha256"]!=EXPECTED_SOURCE_SHA256:
        failures.append("image fingerprint disagrees with V39 source")
    if abs(float(recipe["duration_seconds"])-DURATION)>.001:
        failures.append("duration differs from V39 duration")
    if int(recipe.get("master_size",0))!=720:
        failures.append("image model is validated only for 720x720")
    if int(recipe.get("fps",0))!=24:
        failures.append("24fps generation baseline mismatch")
    if not all(shutil.which(x) for x in ("ffmpeg","ffprobe")):
        warnings.append("local ffmpeg / ffprobe missing (Actions may differ)")
    drawing=quality_gate()
    if not drawing["passed"]:failures.extend(drawing["errors"])
    cues=cue_manifest()
    timing=time_preflight(cues)
    if not timing["pass"]:failures.extend(timing["issues"])
    if timing["timing_is_provisional"]:
        warnings.append("lyric pause timing is provisional, not voice-aligned")
    has_sources=bool(source_image and source_audio)
    audio_duration=None
    if has_sources:
        try:
            check_private_assets(recipe,source_image,source_audio)
            from PIL import Image
            with Image.open(source_image) as picture:
                if picture.size!=(1536,1536):
                    failures.append("original image dimensions changed")
            result=subprocess.run(["ffprobe","-v","error","-show_entries",
                                   "format=duration","-of","json",str(source_audio)],
                                   capture_output=True,text=True,check=True)
            audio_duration=float(json.loads(result.stdout)["format"]["duration"])
            if abs(audio_duration-DURATION)>0.4:
                failures.append("source audio duration does not align to recipe")
        except (OSError,ValueError,subprocess.CalledProcessError) as e:
            failures.append("original asset verification failed: "+type(e).__name__)
    else:
        warnings.append("local originals not supplied to this preflight")
    if len(PHASES)<7 or PHASES[-1][0]!="title":
        failures.append("final title phase is missing")
    result={"version":"V44-no-dropbox-preflight","ready_for_authorized_render":not failures and has_sources,
         "local_sources_verified":has_sources and not failures,
         "audio_duration":audio_duration,
         "checks":{"recipe":True,"drawing_state":drawing["passed"],"cue_map":timing["pass"],
                   "strict_original_sha":has_sources,"titles_only_at_end":PHASES[-1][0]=="title"},
         "warnings":warnings,"failures":failures,
         "rendered_video":False,"image_exported":False,"dropbox_required":False}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image")
    p.add_argument("--audio")
    p.add_argument("--recipe",default="catalog/mv_repeatable_recipe_v1.json")
    p.add_argument("--out",default=None)
    a=p.parse_args()
    result=check(a.image,a.audio,a.recipe)
    if a.out:
        Path(a.out).parent.mkdir(parents=True,exist_ok=True)
        Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    if result["failures"]:raise SystemExit(1)
if __name__=="__main__":main()
