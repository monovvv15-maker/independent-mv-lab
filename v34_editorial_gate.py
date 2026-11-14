"""V34 hard pre-render editorial gate. Does not generate video.
Checks that rejected footage cannot slip into the movie and that proposed
shots visibly advance action/time/emotion, not stock karaoke placeholders.
"""
import json
from pathlib import Path
PLAN=Path("catalog/v34_director_source_decisions.json")
def evaluate(d):
    e=[]
    if d.get("render_authorized") or d.get("video_generated"):e.append("no video rendering before next approval")
    evidence=d["source_evidence"]
    for id,record in evidence.items():
        if "evidence_run" not in record:e.append("missing provenance "+id)
        if record["status"]=="reject" and record.get("approved_for_edit"):e.append("rejected footage approved "+id)
        if record["status"]=="unavailable" and record.get("approved_for_edit"):e.append("unavailable footage approved "+id)
    acts=d["storyboard_revision"]
    if len(acts)<5:e.append("no complete action/time progression")
    for a in acts:
        if not a.get("change") or not a.get("do_not"):e.append("no editorial purpose")
    if d.get("timing")!="all lyric timing unknown; no fake timestamps assigned":e.append("unverified audio timing promoted")
    return {"pass":not e,"evaluated_sources":len(evidence),"render_ready":False,"video_generated":False,"errors":e}
if __name__=="__main__":
    p=json.loads(PLAN.read_text(encoding="utf-8"))
    r=evaluate(p)
    print(json.dumps(r,ensure_ascii=False))
    if r["errors"]:raise SystemExit(1)
