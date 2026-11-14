"""V36 editorial verification. Distinguish cut grammar from verified motion."""
import json
from pathlib import Path
P=Path("scripts/EGACHAN_V36_NO_REPEAT_DIRECTOR_CUT.json")
def validate(data):
    errors=[];seen=set();grammars=set();ids=set()
    scenes=data["scenes"]
    if len(scenes)!=13:errors.append("13 distinct narrative operations required")
    for s in scenes:
        if s["id"] in ids:errors.append("duplicate scene")
        ids.add(s["id"])
        if s["grammar"] in grammars:errors.append("repeated visual grammar "+s["id"])
        grammars.add(s["grammar"])
        for media in s["source"]:
            if media in seen:errors.append("reused source "+media)
            seen.add(media)
        if not s["goal"] or not s["conditional"]:errors.append("unsupported purpose")
    if set(s["chapter"] for s in scenes)!=set(range(1,8)):errors.append("missing 7 chapter flow")
    if data.get("video_generated") or not data.get("no_new_mp4"):errors.append("unauthorized render")
    if not any("foot stops" in x for x in data.get("unresolved_actions",[])):errors.append("false foot stop completion")
    return errors
if __name__=="__main__":
    d=json.loads(P.read_text(encoding="utf-8"))
    e=validate(d)
    print(json.dumps({"pass":not e,"scenes":len(d["scenes"]),"unique_sources":len({m for s in d["scenes"] for m in s["source"]}),"unresolved":d["unresolved_actions"],"video_generated":False,"errors":e},ensure_ascii=False))
    if e:raise SystemExit(1)
