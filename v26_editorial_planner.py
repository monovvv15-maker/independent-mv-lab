"""V26 real (but rule-based) editorial selection engine.
Chapter semantics are curated tags from Pexels listings, NOT machine vision or audio understanding.
It produces a proposed EDL and rejects auto-render until source frames and musical timing are reviewed.
"""
import json
from pathlib import Path

CHAPTERS=[
 (0.0,30.0,{"morning":5,"neighborhood":4,"rain":2,"walking":2}),
 (30.0,65.0,{"rain":5,"street":3,"wind":2,"flower":1}),
 (65.0,99.0,{"people":4,"walking":5,"city":4,"crossing":3}),
 (99.0,134.0,{"memory":5,"old_town":4,"train":4,"street":2}),
 (134.0,168.0,{"stillness":6,"flower":6,"wind":4,"people":1}),
 (168.0,199.872,{"ending":5,"sunset":5,"people":3,"city":2,"neighborhood":2}),
]
MAX_SHOT=8.0
def score(clip,preferences,previous_id,used):
    if clip.get("license_page")!="Free":return -10000
    if not clip.get("duration") or clip["duration"]<4:return -10000
    if clip.get("width") and clip.get("height") and clip["width"]<clip["height"]:return -10000
    if clip.get("fps") and clip["fps"]<23.9:return -10000
    semantic=sum(preferences.get(tag,0) for tag in clip.get("tags",[]))
    distinct=len(set(clip.get("tags",[])) & set(preferences))
    repeat=used.get(clip["id"],0)
    return semantic*10+distinct*3-repeat*22-(40 if previous_id==clip["id"] else 0)
def propose(catalog,chapters=CHAPTERS):
    shots=[];used={};prev=None
    for ch,(start,end,keywords) in enumerate(chapters,1):
        cursor=start
        while cursor<end-0.001:
            eligible=[clip for clip in catalog if
                any(keywords.get(tag,0)>0 for tag in clip.get("tags",[]))
                and score(clip,keywords,None,{})>=0]
            choices=sorted(eligible,key=lambda c:(-score(c,keywords,prev,used),c["id"]))
            if not choices:
                raise ValueError("No semantically eligible footage in chapter "+str(ch))
            chosen=choices[0]
            dur=min(MAX_SHOT,float(chosen["duration"]),end-cursor)
            shots.append({"chapter":ch,"start":round(cursor,3),"end":round(cursor+dur,3),
              "clip_id":chosen["id"],"source_url":chosen["url"],"tags":chosen["tags"],
              "reason":"chapter tag match; repeat penalty applied","visual_review":"pending",
              "musical_sync":"pending","ready_for_render":False})
            used[chosen["id"]]=used.get(chosen["id"],0)+1
            prev=chosen["id"];cursor+=dur
    return shots
def inspect(plan):
    violations=[];last=0
    for shot in plan:
        if abs(shot["start"]-last)>0.002:violations.append("gap/overlap")
        if shot["end"]<=shot["start"]:violations.append("bad shot duration")
        last=shot["end"]
    if abs(last-199.872)>0.002:violations.append("not full song")
    return violations
def main():
    folder=Path("discovery_output");folder.mkdir(exist_ok=True)
    catalog=json.loads(Path("catalog/v26_full_length_candidates.json").read_text(encoding="utf8"))["items"]
    shots=propose(catalog)
    report={"engine":"V26 tag-based editorial planner, not AI vision or beat-sync",
      "duration_seconds":199.872,"cuts":len(shots),"unique_source_ids":len(set(x["clip_id"] for x in shots)),
      "errors":inspect(shots),"render_ready":False,"source_video_downloaded":False,
      "song_lyric_sync_verified":False,"plan":shots}
    (folder/"v26_proposed_edl.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({k:v for k,v in report.items() if k!="plan"},ensure_ascii=False))
    if report["errors"]:raise SystemExit(1)
if __name__=="__main__":main()
