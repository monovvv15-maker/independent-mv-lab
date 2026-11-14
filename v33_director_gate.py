"""V33 semantic edit-decision gate. Fails rather than filling gaps with repeated stock.
Does not generate frames, audio, or video. Intended for 199.872s full song.
"""
import json
from pathlib import Path
PLAN=Path("catalog/v33_narrative_shot_plan.json")
ARC=["present_departure","rain_memory","present_movement","past_present_comparison","permission_to_pause","small_discovery","open_future"]
def validate(data):
    errors=[]
    shots=data.get("shots",[])
    if data.get("narrative_arc")!=ARC:errors.append("narrative arc invalid")
    if len(shots)<20:errors.append("too few story actions")
    if not shots or shots[0]["visual"]!="靴を手に取る":errors.append("not opening on shoes")
    if shots and shots[-1]["role"]!="future":errors.append("future not shown")
    seen={}
    actions=set()
    for index,s in enumerate(shots):
        ident=s["source_id"]
        if ident in seen and not str(ident).startswith("missing-"):
            errors.append(f"reused source: {ident} shots {seen[ident]} and {s['shot_id']}")
        seen[ident]=s["shot_id"]
        if not s.get("meaning") or not s.get("role"):errors.append("shot has no meaning "+str(index))
        if s.get("final_authorized"):errors.append("premature shot approval "+str(index))
        if s.get("time_start") is not None or s.get("time_end") is not None:
            errors.append("unverified timing asserted "+str(index))
        actions.add(s["role"])
    if not {"action","comparison","pause","discovery","future"}.issubset(actions):
        errors.append("missing life progression")
    if data.get("video_generated"):errors.append("video generated without explicit approval")
    return errors

def status(data):
    missing=[s["shot_id"] for s in data["shots"] if s["source_status"]=="missing"]
    return {"script_qa":not validate(data),"shots":len(data["shots"]),
            "missing_scene_ids":missing,"missing_count":len(missing),
            "ready_to_render":not missing and not validate(data) and False,
            "audio_lyric_sync_verified":False,"video_generated":False,
            "issues":validate(data)}

if __name__=="__main__":
    report=status(json.loads(PLAN.read_text(encoding="utf-8")))
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    (out/"v33_director_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["issues"]:raise SystemExit(1)
