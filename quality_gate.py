"""Conservative editorial quality gate for the pilot song.
This checks metadata only; final content still needs human video review.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

SCENE_QUERIES = {
  "morning street": ("morning", "street"),
  "rain puddles": ("rain", "puddle"),
  "shoes door": ("shoes", "door"),
  "walking street": ("walking", "street"),
  "window wind": ("window", "wind"),
  "sunlit neighborhood": ("sunlit", "neighborhood"),
}
EXCLUDE = {"wildfire", "fire", "explosive", "meeting", "simulation", "gaming", "zoo", "bear", "train", "subway", "elevator", "prada", "cloud streets"}

def valid_for_scene(item):
    query = item.get("search_query", "")
    title = str(item.get("title", "")).lower()
    if not item.get("license_ok"):
        return False
    if query not in SCENE_QUERIES:
        return False
    if any(word in title for word in EXCLUDE):
        return False
    # A conservative title-level filter; search matches alone are not evidence.
    tokens = SCENE_QUERIES[query]
    return all(token in title for token in tokens)

def audit(catalog):
    by_scene = defaultdict(list)
    for row in catalog:
        if valid_for_scene(row):
            by_scene[row["search_query"]].append(row)
    scenes = []
    for q in SCENE_QUERIES:
        scenes.append({"scene":q,"accepted":len(by_scene[q]),"candidates":[{"title":r.get("title"),"source_url":r.get("source_url"),"license":r.get("license"),"author":r.get("author")} for r in by_scene[q]]})
    return {"total":len(catalog),"metadata_relevant":sum(x["accepted"] for x in scenes),"covered_scenes":sum(x["accepted"]>0 for x in scenes),"total_scenes":len(scenes),"scenes":scenes,
            "note":"Metadata relevance only. Human visual and CC attribution review mandatory."}

def main():
    folder=Path("discovery_output")
    catalog=json.loads((folder/"catalog.json").read_text(encoding="utf-8"))
    result=audit(catalog)
    (folder/"quality_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"total":result["total"],"metadata_relevant":result["metadata_relevant"],"covered_scenes":result["covered_scenes"],"total_scenes":result["total_scenes"]}))
    if result["covered_scenes"] < 4:
        raise SystemExit("Quality gate FAIL: insufficient distinct scenes for reliable 30-second MV")

if __name__=="__main__":main()
