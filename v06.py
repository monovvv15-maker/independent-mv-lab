"""V06 strict scene-based Wikimedia Commons video search. Metadata only."""
import json,re
from pathlib import Path
from media_sources import commons_search
from review import build_review
SCENES={
 "01_morning": (["intitle:morning street","intitle:sunrise road","intitle:morning walking"],("morning","sunrise","dawn"),("street","road","city","town","walk","drive")),
 "02_rain": (["intitle:rain street","intitle:puddle","intitle:rainy city"],("rain","puddle","wet"),()),
 "03_door": (["intitle:shoes door","intitle:footsteps","intitle:doorstep"],("shoe","footstep"),("shoe","door","walking","feet")),
 "04_walking": (["intitle:walking street","intitle:walking town","intitle:walk rural"],("walk","stroll"),("street","town","rural","path","sidewalk","city","road")),
 "05_window": (["intitle:window rain","intitle:leaves wind","intitle:trees wind"],("window","leaf","leaves","tree"),("rain","wind","window","trees","leaves","breeze")),
 "06_sunshine": (["intitle:sunny street","intitle:sunlight town","intitle:morning neighborhood"],("sunny","sunlight","sunshine","morning"),("street","town","neighborhood","city","road"))
}
BLOCK=("wildfire","explosive","simulation","meeting","zoo","bear","subway","video game","cloud street","planet","nebula","star formation","volcano","prime minister","council","nato summit","department of energy","hurricane","destruction","cyberpunk","hailuo ai","cats soak","night on foot")
def relevant(title, scene):
    title=re.sub(r"[^a-z0-9]+"," ",title.lower())
    if any(b in title for b in BLOCK):return False
    _,terms,context=SCENES[scene]
    return any(t in title for t in terms) and (not context or any(t in title for t in context))
def discover(limit=8, search_fn=None):
    search_fn=search_fn or commons_search
    scenes,errors={},[]
    for scene,(queries,_,__) in SCENES.items():
        found={}
        for q in queries:
            try:
                for item in search_fn(q,limit=limit):
                    if item.get("license_ok") and relevant(item.get("title",""),scene):
                        entry=dict(item);entry["scene_id"]=scene;entry["matched_query"]=q;found[entry["id"]]=entry
            except Exception as exc:
                errors.append({"scene":scene,"query":q,"error":str(exc)[:200]})
        scenes[scene]=list(found.values())
    return scenes,errors
def main():
    output=Path("discovery_output");output.mkdir(exist_ok=True)
    scenes,errors=discover()
    items=[x for vals in scenes.values() for x in vals]
    report={"scene_counts":{k:len(v) for k,v in scenes.items()},"covered_scenes":sum(bool(v) for v in scenes.values()),"unique_clips":len(set(x["id"] for x in items)),"errors":errors,"notice":"Metadata only; review frames, credits and source license before use"}
    (output/"v06_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (output/"v06_candidates.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
    build_review(items,output/"v06_review.html")
    print(json.dumps(report,ensure_ascii=False))
    if report["covered_scenes"]<4:raise SystemExit("QUALITY FAIL: fewer than 4 scenes covered")
if __name__=="__main__":main()
