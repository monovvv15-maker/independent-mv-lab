"""V32 STORY-FIRST full-length rough, explicitly creator-authorized 2026-11-14.
The seven-chapter V29 script is the source of edit meaning. This is not verified
word-level lyric alignment; the author will judge the produced full-length rough.
No original music uploaded to public GitHub. No original files overwritten.
"""
import argparse, json, subprocess, tempfile
from pathlib import Path
from v18_pexels_review import get_video
from v28_full_renderer import duration_of, source_offset, ffmpeg_bin, concat_command
from v31_renderer_adapter import graded_trim_command, validate_command

SONG_LENGTH=199.872
# Real Pexels footage already sampled in V23/V26/V28; chapter grouping is deliberate.
CHAPTERS=[
 ("01_shoes_present",25.0,[(4953053,8),(40456181,9),(13749224,8)]),
 ("02_yesterday_rain",30.0,[(13749224,8),(40456181,8),(31432212,7),(4435691,7)]),
 ("03_walk_again",30.0,[(4464905,8),(3998656,8),(34892787,7),(37601314,7)]),
 ("04_past_me_now_me",30.0,[(34506423,7),(40409379,8),(3723683,8),(7312217,7)]),
 ("05_pausing_is_ok",35.0,[(12769743,8),(10695941,11),(37108132,8),(4435691,8)]),
 ("06_notice_small_joy",30.0,[(10695941,8),(4435691,7),(40456181,8),(37601314,7)]),
 ("07_let_it_be_future",19.872,[(40456181,7),(3998656,6),(37541865,6.872)])
]
# Checked canonical free-download endpoints: no guessed CDN.
ids={clip for _,_,shots in CHAPTERS for clip,_ in shots}
SOURCE_PAGES={
 4953053:"low-angle-view-of-a-person-putting-on-the-shoe-and-tying-it",
 40456181:"quiet-suburban-neighborhood-in-spring",
 13749224:"rainfall-over-puddle",
 31432212:"vintage-suburban-street-with-classic-vibes",
 4435691:"windy-day-in-spring",
 4464905:"person-walking-on-concrete-floor",
 3998656:"close-up-shot-of-a-man-walking",
 34892787:"busy-pedestrian-crossing-in-urban-city-scene",
 37601314:"casual-pedestrian-foot-traffic-in-urban-setting",
 34506423:"woman-enjoying-fresh-morning-air-by-window",
 40409379:"charming-old-city-street-with-historic-architecture",
 3723683:"people-walking-on-the-street",
 7312217:"old-buildings-in-the-street-of-warsaw-poland",
 12769743:"pedestrians-waiting-to-cross-a-busy-city-street",
 10695941:"flowers-and-grasses-waving-on-wind",
 37108132:"urban-street-scene-with-passing-train",
 37541865:"scenic-sunset-over-city-skyline"
}
def story_check():
    issues=[]
    if len(CHAPTERS)!=7:issues.append("must have 7 chapters")
    if CHAPTERS[0][2][0][0]!=4953053:issues.append("opening not shoes")
    if abs(sum(c[1] for c in CHAPTERS)-SONG_LENGTH)>0.001:issues.append("duration mismatch")
    if len(SOURCE_PAGES)!=len(ids):issues.append("unlisted source")
    for name,length,shots in CHAPTERS:
        if abs(sum(sec for _,sec in shots)-length)>0.001:issues.append(name+" cut lengths mismatch")
        if any(sec<1 or sec>11 for _,sec in shots):issues.append(name+" invalid shot length")
    return issues

def render(output):
    issues=story_check()
    if issues:raise ValueError(issues)
    exe=ffmpeg_bin()
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); videos={};durations={}
        for clip in sorted(ids):
            page="https://www.pexels.com/video/"+SOURCE_PAGES[clip]+"-"+str(clip)+"/"
            file=root/(str(clip)+".mp4")
            print("Fetch:",clip,flush=True)
            get_video({"download":f"https://www.pexels.com/download/video/{clip}/","page":page},file)
            videos[clip]=file
            durations[clip]=duration_of(file,exe)
        segdir=root/"segments";segdir.mkdir()
        parts=[];used={};cursor=0.
        for name,length,shots in CHAPTERS:
            for clip,sec in shots:
                n=used.get(clip,0);used[clip]=n+1
                if durations[clip]<sec-0.15:raise ValueError("Source too short "+str(clip))
                # Offset repeated source excerpts so the same portion is not copied again.
                pos=source_offset(n,durations[clip],sec)
                part=segdir/(f"{len(parts):03d}.mp4")
                cmd=graded_trim_command(exe,videos[clip],part,pos,sec)
                validate_command(cmd)
                print(f"Render: {name} clip={clip} {cursor:.3f}-{cursor+sec:.3f}",flush=True)
                subprocess.run(cmd,check=True,timeout=110)
                if not part.is_file() or part.stat().st_size<1000:raise RuntimeError("Bad segment "+str(part))
                parts.append(part);cursor+=sec
        playlist=root/"join.txt"
        playlist.write_text("".join("file '"+str(p)+"'\n" for p in parts),encoding="utf-8")
        subprocess.run(concat_command(exe,playlist,Path(output).resolve()),check=True,timeout=180)
    out=Path(output)
    if out.stat().st_size<200000:raise RuntimeError("bad final output")
    print(json.dumps({"generated":True,"seconds_expected":SONG_LENGTH,"chapters":7,"shots":len(parts),"sources":len(ids),"silent":True,"size_bytes":out.stat().st_size},ensure_ascii=False),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authorize-render",action="store_true")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    if not a.authorize_render:raise SystemExit("Video-generation approval missing")
    render(a.output)
if __name__=="__main__":main()
