"""V29 canonical storyboard and selective media mapping QA. No rendering."""
import json
from pathlib import Path
SCRIPT=Path("scripts/EGACHAN_V29_CANONICAL_STORYBOARD_20261114.md")
MAPPING=Path("catalog/v29_script_based_asset_map.json")

def check():
    script=SCRIPT.read_text(encoding="utf-8")
    data=json.loads(MAPPING.read_text(encoding="utf-8"))
    errors=[]
    for s in ["主題","立ち止まることには意味がある","靴を履く","第7章","過去の写真"]:
        if s not in script:errors.append("canonical script missing "+s)
    chapters=data["chapters"]
    if len(chapters)!=7:errors.append("not seven chapters")
    last=0.0
    for i,ch in enumerate(chapters,1):
        if ch["chapter"]!=i:errors.append(f"misnumbered {i}")
        if abs(ch["provisional_start"]-last)>0.01:errors.append(f"timeline gap {i}")
        if ch["provisional_end"]<=ch["provisional_start"]:errors.append(f"invalid duration {i}")
        if not ch.get("required"):errors.append(f"no story needs {i}")
        if not ch.get("priority_existing_video_ids"):errors.append(f"not mapped {i}")
        last=ch["provisional_end"]
    if abs(last-199.872)>0.001:errors.append("full duration mismatch")
    if data.get("render_authorized"):errors.append("render not authorized")
    if data.get("lyric_timestamps_verified"):errors.append("unverified lyric timestamps claimed verified")
    if data["policy"]["use_all"]:errors.append("do not force every clip into film")
    if not data["policy"]["reuse_existing_photos"]:errors.append("photo reuse omitted")
    if data["policy"]["unknown_photo_inventory"]!="not yet enumerated":errors.append("unverified photo inventory")
    if 4953053 not in chapters[0]["priority_existing_video_ids"]:errors.append("shoe opening lost")
    return {"valid":not errors,"chapters":len(chapters),"total_seconds":last,
            "photo_inventory":"not independently verified","video_generated":False,"errors":errors}

if __name__=="__main__":
    r=check();print(json.dumps(r,ensure_ascii=False))
    if not r["valid"]:raise SystemExit(1)
