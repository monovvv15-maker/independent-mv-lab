"""V30 script-first visual preflight. Never renders."""
import json
from pathlib import Path
RECIPE=Path("catalog/v30_story_first_edit_recipe.json")
STYLE=Path("scripts/EGACHAN_V30_PAST_PRESENT_FUTURE_STYLE_20261114.md")
def inspect():
 d=json.loads(RECIPE.read_text(encoding="utf-8"))
 style=STYLE.read_text(encoding="utf-8")
 faults=[]
 if len(d["chapter_assets"])!=7:faults.append("chapter count")
 if d["render_authorized"] or d["new_mp4_generated"]:faults.append("render gate violated")
 if d["render_start_phrase"]!="動画作成":faults.append("incorrect author approval phrase")
 if 4953053 not in d["chapter_assets"][0]["primary_ids"]:faults.append("shoe opening missing")
 if 34506423 not in d["chapter_assets"][0]["negative_ids"]:faults.append("unwanted woman opening not excluded")
 if d["editing"]["lyric_sync"]!="unverified":faults.append("unverified vocal timing claimed verified")
 if any(x not in style for x in ["過去の自分","今の自分","立ち止まって","IMG_6807.jpeg"]):faults.append("style semantics missing")
 return {"pass":not faults,"chapters":len(d["chapter_assets"]),"video_generated":False,"errors":faults}
if __name__=="__main__":
 print(json.dumps(inspect(),ensure_ascii=False))
 if not inspect()["pass"]:raise SystemExit(1)
