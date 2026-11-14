"""V15 candidate suitability checks based on independently verified provider metadata.
This never marks a video visually approved.
"""
import json
from pathlib import Path

def evaluate_candidate(item):
    issues=[]
    w,h=item.get("width"),item.get("height")
    if not w or not h:issues.append("dimensions unknown")
    elif w < h:issues.append("vertical footage: 16:9 crop requires individual review")
    fps=item.get("fps")
    if fps is None:issues.append("fps unknown")
    elif fps < 23.9:issues.append("low source frame rate")
    length=item.get("duration")
    if length is None:issues.append("duration unknown")
    elif length < 5:issues.append("too short for planned 5-second scene")
    if item.get("visual_review")!="approved":
        issues.append("full-motion visual review missing")
    return {"id":item["id"],"scene":item["scene"],"geometry_preference":bool(w and h and w>=h and fps is not None and fps>=23.9 and length is not None and length>=5),"render_approved":False,"issues":issues}

def main():
    src=json.loads(Path("v15_pexels_candidate_manifest.json").read_text(encoding="utf-8"))
    report=[evaluate_candidate(item) for item in src["candidates"]]
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    (out/"v15_candidate_preflight.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"candidates":len(report),"geometry_preferred":sum(x["geometry_preference"] for x in report),"render_approved":0,"shoe_landscape_candidate":any(x["scene"]=="03_shoes" and x["geometry_preference"] for x in report)},ensure_ascii=False))
if __name__=="__main__":main()
