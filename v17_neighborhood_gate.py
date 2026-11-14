"""V17 landscape candidate metadata check, not an audiovisual approval."""
import json
from pathlib import Path
def check(rows):
    out=[]
    for c in rows:
        issues=[]
        if c["width"]<=c["height"]:issues.append("not landscape")
        if c["duration_sec"]<5:issues.append("shorter than planned segment")
        if c["fps"]<23.9:issues.append("below preferred source fps")
        if c["license_page"]!="Pexels Free":issues.append("license unresolved")
        if c["visual_status"]!="approved":issues.append("actual video not inspected")
        out.append({"id":c["id"],"metadata_compatible":not any(i!="actual video not inspected" for i in issues),"render_approved":not issues,"issues":issues})
    return out
if __name__=="__main__":
    d=json.loads(Path("v17_landscape_candidates.json").read_text(encoding="utf-8"))
    rows=check(d["scenes"])
    folder=Path("discovery_output");folder.mkdir(exist_ok=True)
    (folder/"v17_neighborhood_gate.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"landscape_candidates":sum(r["metadata_compatible"] for r in rows),"visual_approved":sum(r["render_approved"] for r in rows)},ensure_ascii=False))
