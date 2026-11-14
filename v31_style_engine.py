"""V31 storyboard-first grading and cut validation. Preflight only: no image/movie export.
Color constants sampled from creator's jacket IMG_6807.jpeg; JPEG stays private.
"""
import json
from pathlib import Path

TARGET={
 "sky_median_rgb":[189,192,201],
 "road_median_rgb":[165,144,127],
 "overall_median_rgb":[179,167,163],
 "description":"soft post-rain blue-grey with faded warm road; never force a false season"
}
def filter_chain():
    # Keep skins, don't force all scenery into monochrome. Avoid simulated scratches.
    return ("eq=contrast=0.91:brightness=0.018:saturation=0.82,"
            "colorbalance=rs=0.01:gs=0.005:bs=0.018:rm=0.005:bm=0.006,"
            "noise=alls=2:allf=t")
def chapter_pacing():
    return [
      {"chapter":1,"aim":"footwear introduction","repetition_cap":1,"transition":"straight"},
      {"chapter":2,"aim":"yesterday's rain","repetition_cap":1,"transition":"reflection match"},
      {"chapter":3,"aim":"current footsteps","repetition_cap":1,"transition":"directional cut"},
      {"chapter":4,"aim":"then and now, world echoes","repetition_cap":1,"transition":"shape match"},
      {"chapter":5,"aim":"permitted stillness","repetition_cap":1,"transition":"long held shot"},
      {"chapter":6,"aim":"noticing flowers","repetition_cap":1,"transition":"eye-line cut"},
      {"chapter":7,"aim":"unforced future","repetition_cap":1,"transition":"visual callback"}
    ]
def validate():
    story=Path("scripts/EGACHAN_V29_CANONICAL_STORYBOARD_20261114.md").read_text(encoding="utf-8")
    new=Path("scripts/EGACHAN_V30_PAST_PRESENT_FUTURE_STYLE_20261114.md").read_text(encoding="utf-8")
    candidate=json.loads(Path("catalog/v31_gap_candidates.json").read_text(encoding="utf-8"))
    errors=[]
    if "靴を履く" not in story:errors.append("opening story missing")
    if "過去の自分" not in new:errors.append("time motif missing")
    if len(chapter_pacing())!=7:errors.append("chapter count")
    if not any(c["scene"]=="small_white_flower" for c in candidate["candidates"]):errors.append("flower gap")
    if "allf=t" not in filter_chain():errors.append("grain missing")
    return {"pass":not errors,"filter":filter_chain(),"reference_rgb":TARGET,
            "chapters":chapter_pacing(),"source_footage_downloaded":False,
            "music_word_timestamps_verified":False,"video_generated":False,"errors":errors}
if __name__=="__main__":
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    report=validate()
    (out/"v31_preflight.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"pass":report["pass"],"chapters":len(report["chapters"]),"render":False,"errors":report["errors"]},ensure_ascii=False))
    if not report["pass"]:raise SystemExit(1)
