"""V35 Director QA: no karaoke-fill, no source reuse, no unsupported motion claims.
Pre-render only. Does not allocate fake lyric timings or render assets.
"""
import json
from pathlib import Path

PATH=Path("catalog/v35_story_continuity_working_plan.json")
ARC=["present_departure","rain_memory","present_movement",
     "past_present_comparison","permission_to_pause","small_discovery","open_future"]
ACTION_REQUIREMENTS={
 "S03":"feet visibly cross the house threshold",
 "S08":"camera follows actual turning of the corner",
 "S14":"two perspectives of different life eras are clearly expressed",
 "S16":"moving foot demonstrably comes to a full stop",
 "S20":"small real flower is shown next to ordinary road, not an impressive flower garden",
 "S21":"visual attention turns toward the roadside flower",
 "S24":"framing clearly advances forward toward an unfamiliar road"
}
def audit(plan):
    failures=[]
    shots=plan["shots"]
    if plan["narrative_arc"]!=ARC:failures.append("narrative order invalid")
    if len(shots)!=25:failures.append("unexpected shot count")
    if shots[0]["source_id"]!="4953053":failures.append("shoe opening lost")
    if plan.get("video_generated"):failures.append("render prematurely claimed")
    seen={}
    for shot in shots:
        src=str(shot["source_id"])
        if not src.startswith("missing-"):
            if src in seen: failures.append("repeat of "+src)
            seen[src]=shot["shot_id"]
        if shot["time_start"] is not None or shot["time_end"] is not None:
            failures.append("unverified cue timestamp "+shot["shot_id"])
        if not shot["meaning"]:failures.append("empty causal role "+shot["shot_id"])
        if shot["source_status"]=="missing" and shot["shot_id"] not in ACTION_REQUIREMENTS and not src.startswith("missing"):
            failures.append("ambiguous missing status "+shot["shot_id"])
    if shots[0]["chapter"]!=1 or shots[-1]["chapter"]!=7:failures.append("life arc bounds")
    if "4376498" in seen and "27571663" not in seen:
        failures.append("sprout foreshadowing without actual flower")
    # Low pixel movement can mean that the actor has already left the frame.
    # Pexels 4464905 at 5s-8s was visually checked and shows empty pavement.
    stop_shot=next((s for s in shots if s["shot_id"]=="S16"),None)
    if stop_shot and str(stop_shot["source_id"])=="4464905":
        failures.append("false foot stop: source 4464905 shows empty pavement at quiet interval")
    selected=[s["shot_id"] for s in shots if s["source_status"]=="real_three_frame_review_candidate"]
    missing=[s["shot_id"] for s in shots if s["source_status"]=="missing"]
    return {"code_qa_pass":not failures,"shot_count":len(shots),"candidate_photo_video_count":len(shots)-len(missing),
      "real_three_frame_candidates":selected,"unfilled_action_shots":missing,
      "unfilled_count":len(missing),"render_ready":False,"lyrics_word_timing_verified":False,
      "music_video_generated":False,"failures":failures,"hard_requirements":ACTION_REQUIREMENTS}

if __name__=="__main__":
    report=audit(json.loads(PATH.read_text(encoding="utf-8")))
    folder=Path("discovery_output");folder.mkdir(exist_ok=True)
    (folder/"v35_director_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("hard_requirements",)},ensure_ascii=False))
    if report["failures"]:raise SystemExit(1)
