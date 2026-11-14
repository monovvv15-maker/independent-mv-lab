"""V10 conservative editorial readiness gate.
No new images, video or audio are generated.
"""
import json
from pathlib import Path

BLOCKED_NOTES = ("sunset mismatch","highway—not neighborhood","bright but not streets")
def evaluate(rows):
    results=[]
    for cue in rows:
        shot=cue.get("recommendation")
        reasons=[]
        if not shot: reasons.append("No candidate")
        else:
            issues=" ".join(shot.get("issues",[])).lower()
            if "sunset" in issues: reasons.append("Sunset scene contradicts morning")
            if "highway" in issues: reasons.append("Highway does not depict neighborhood")
            if "low source fps" in issues: reasons.append("15fps source fails 24fps preferred quality")
            if "not an actual street" in issues: reasons.append("No actual street pictured")
            if shot.get("visual_review")!="approved":reasons.append("Footage frames not personally reviewed")
        if cue.get("timing_status")!="VERIFIED":reasons.append("Audio/song cue timing not verified")
        results.append({
            "start":cue["start"],"end":cue["end"],"scene":cue["scene"],
            "candidate":shot.get("title") if shot else None,
            "status":"BLOCKED" if reasons else "READY",
            "reasons":reasons
        })
    return {"render_ready":all(x["status"]=="READY" for x in results),
            "visual_verified":sum(x["status"]=="READY" for x in results),
            "items":results,
            "warning":"This is a metadata and QA preflight, not visual content recognition."}

def main():
    out=Path("discovery_output")
    rows=json.loads((out/"v09_storyboard.json").read_text(encoding="utf-8"))
    report=evaluate(rows)
    (out/"v10_preflight.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"render_ready":report["render_ready"],"blocked_cues":sum(x["status"]=="BLOCKED" for x in report["items"]),"reasons":report["items"]},ensure_ascii=False))
    # Successful execution of preflight != authorization to render.
if __name__=="__main__":main()
