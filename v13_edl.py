"""V13 reproducible rendering preflight and safe edit-decision list (EDL).
No media is generated or downloaded here.
"""
import json
from pathlib import Path

MIN_FPS=23.9  # Accept cinema 23.976/23.98 source; convert output to 30fps
TARGET_SECONDS=30
def check_edl(edl):
    errors=[]
    if not isinstance(edl,list) or not edl:
        return ["EDL missing"]
    ordered=sorted(edl,key=lambda x:x["start"])
    previous_end=0.0
    people=set()
    for item in ordered:
        start,end=float(item["start"]),float(item["end"])
        if abs(start-previous_end)>0.02:errors.append(f"gap or overlap at {start}")
        if end<=start:errors.append(f"invalid scene duration at {start}")
        previous_end=end
        if not item.get("license_verified"):errors.append(f"{start}s rights not verified")
        if item.get("visual_review")!="approved":errors.append(f"{start}s not visually approved")
        if item.get("audio_sync")!="verified":errors.append(f"{start}s audio sync unverified")
        if float(item.get("source_fps",0))<MIN_FPS:errors.append(f"{start}s under 24fps")
        if not item.get("full_video_downloaded"):errors.append(f"{start}s original video missing")
        if not item.get("crop_approved"):errors.append(f"{start}s 16:9 crop unapproved")
        who=item.get("protagonist")
        if who and who!="no_person":people.add(who)
    if abs(previous_end-TARGET_SECONDS)>0.02:errors.append("not 30 seconds")
    if len(people)>1:errors.append("mixed protagonist identity")
    return errors

def make_draft():
    # Explicitly NOT real vocal times. The arrangement must be aligned by ear.
    scenes=[
        ("01_morning","mixkit-1",15,"intro: morning light"),
        ("02_rain","mixkit-4",24,"rain memory / puddle"),
        ("03_door",None,0,"shoes being put on: missing accepted footage"),
        ("04_walking","mixkit-7",24,"walking through crosswalk"),
        ("05_window","mixkit-8",24,"morning window opening"),
        ("06_sunshine",None,0,"same morning neighborhood: needs new footage"),
    ]
    result=[]
    for i,(scene,clip,fps,description) in enumerate(scenes):
        result.append({"start":i*5,"end":(i+1)*5,"scene":scene,"candidate_id":clip,
                       "description":description,"license_verified":bool(clip),
                       "visual_review":"pending","audio_sync":"unverified",
                       "source_fps":fps,"full_video_downloaded":False,
                       "crop_approved":False,"protagonist":"no_person",
                       "time_basis":"illustrative 5-second slots, NOT vocal timings"})
    return result

if __name__=="__main__":
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    draft=make_draft()
    errors=check_edl(draft)
    (out/"v13_edl_draft.json").write_text(json.dumps(draft,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"v13_render_blockers.json").write_text(json.dumps({"render_ready":False,"blocker_count":len(errors),"blockers":errors},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"v13_edl_segments":len(draft),"render_ready":False,"blocker_count":len(errors)},ensure_ascii=False))
