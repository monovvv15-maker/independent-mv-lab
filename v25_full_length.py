"""V25 whole-song editorial plan. Time ranges are CHAPTERS, NOT lyric boundaries.
No actual image/video render is performed here. No private audio is uploaded.
"""
import json
from pathlib import Path
DURATION=199.872
CHAPTERS=[
 {"start":0.0,"end":30.0,"name":"世界各地の朝が始まる","shots":["住宅街の朝","雨上がりの路面","靴を履く手元","別の人が歩き出す","窓を開く","木立のある街"],"footage":"v23 partly verified","lyric_alignment":"unverified"},
 {"start":30.0,"end":65.0,"name":"昨日の雨と、今日の光","shots":["別の国の路地","窓の水滴","傘を閉じる人","路面の反射","朝の光と歩道"],"footage":"needs source verification","lyric_alignment":"unverified"},
 {"start":65.0,"end":99.0,"name":"異なる街、同じ歩幅","shots":["アジアの住宅街","ヨーロッパの通学路","街角の挨拶","靴音に合わせた切替","風に揺れる木"],"footage":"needs source verification","lyric_alignment":"unverified"},
 {"start":99.0,"end":134.0,"name":"変わっていく街と記憶","shots":["古い道と新しい建物","踏切または信号","遠景へ進む人","過去を思わせる空席","歩き続ける足元"],"footage":"needs source verification","lyric_alignment":"unverified"},
 {"start":134.0,"end":168.0,"name":"立ち止まることも大切","shots":["静止する足元","路傍の花","風に吹かれる人物の背中","曇天から日差しへ","顔の見えない微笑み"],"footage":"needs source verification","lyric_alignment":"unverified"},
 {"start":168.0,"end":199.872,"name":"明日もそれぞれの朝へ","shots":["世界各地の朝のモンタージュ","誰かとすれ違う","雨粒に光","空を見上げる","静かな街の余韻"],"footage":"needs source verification","lyric_alignment":"unverified"},
]
def validate(chapters=CHAPTERS):
 errors=[];last=0.0
 for i,ch in enumerate(chapters):
  if abs(ch["start"]-last)>0.001:errors.append(f"gap or overlap at chapter {i}")
  if ch["end"]<=ch["start"]:errors.append(f"negative chapter duration at {i}")
  if not ch.get("shots"):errors.append(f"missing visual ideas at {i}")
  last=ch["end"]
 if abs(last-DURATION)>0.001:errors.append("song duration mismatch")
 return errors
def status():
 return {"version":"V25","total_seconds":DURATION,"verified_song_sha256":"d6615b1116569d603e2e630db9b08da0b065cd8208f877bb04c1d3ad63057764","story":"global everyday mornings","chapters":CHAPTERS,"timing_status":"provisional narrative chapters, not lyric alignment","render_ready":False,"video_generated":False,"missing":["new verified footage for chapters 2–6","manual or listening-confirmed lyric timing for whole song","full-length quality review before publication"]}
if __name__=="__main__":
 out=Path("discovery_output");out.mkdir(exist_ok=True)
 (out/"v25_whole_song_plan.json").write_text(json.dumps(status(),ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"chapters":len(CHAPTERS),"duration":DURATION,"errors":validate(),"render_ready":False,"video_generated":False},ensure_ascii=False))
 if validate():raise SystemExit(1)
