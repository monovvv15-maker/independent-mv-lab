"""V09 editorial preflight: propose 30s sequence from license-cleared V08 metadata.

Important: this is NOT a visual review and NOT a render approval. A human
must visually approve every clip and verify that the song timing is correct.
"""
import json
from html import escape
from pathlib import Path

CUES=[
 {"start":0,"end":5,"scene":"01_morning","intent":"雨上がりの朝、空気感を見せる"},
 {"start":5,"end":10,"scene":"02_rain","intent":"昨日の雨の余韻、反射や水滴"},
 {"start":10,"end":15,"scene":"03_door","intent":"出かける準備、足元"},
 {"start":15,"end":20,"scene":"04_walking","intent":"一歩目、歩く動作"},
 {"start":20,"end":25,"scene":"05_window","intent":"窓から風が入り、日常が動き出す"},
 {"start":25,"end":30,"scene":"06_sunshine","intent":"明るい朝の余韻、街へ"},
]
def assess(row, cue):
    """Conservative metadata-only scoring, not computer vision."""
    if not row.get("eligible") or row.get("scene")!=cue["scene"]:
        return None
    duration=float(row.get("duration",0))
    fps=float(row.get("fps",0))
    if duration<cue["end"]-cue["start"]:return None
    note=(row.get("note") or "").lower()
    score=100
    issues=[]
    if fps<24:score-=18;issues.append("low source fps")
    if "sunset" in note:score-=35;issues.append("sunset conflicts with morning")
    if "highway" in note:score-=25;issues.append("highway rather than neighborhood")
    if "afternoon" in note:score-=12;issues.append("afternoon color mismatch")
    if "autumn" in note:score-=15;issues.append("seasonal color mismatch")
    if "not actual street" in note or "not streets" in note:
        score-=20;issues.append("not an actual street")
    if "color review" in note:score-=10;issues.append("color review needed")
    return {"id":row["id"],"url":row["url"],"title":row["title"],"score":score,"duration":duration,"fps":fps,"issues":issues,"visual_review":"pending"}
def plan(rows):
    result=[]
    for cue in CUES:
        options=[sc for r in rows if (sc:=assess(r,cue)) is not None]
        options.sort(key=lambda x:(-x["score"],x["id"]))
        result.append({**cue,"recommendation":options[0] if options else None,"alternatives":options[1:],"status":"UNVERIFIED_VISUAL","timing_status":"PROVISIONAL"})
    return result
def main():
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    rows=json.loads((out/"v08_license_audit.json").read_text(encoding="utf-8"))
    result=plan(rows)
    (out/"v09_storyboard.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    html=['<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:15px system-ui;background:#141414;color:#eee;padding:16px}article{padding:14px;margin:14px 0;background:#252525;border-radius:12px}a{color:#ade1ff}small{color:#ffdf8e}</style><h1>V09 30秒MV 演出台本（仮）</h1><p>動画の内容は未確認。下記は素材ページへのリンクのみ。正確な音同期も未確認。</p>']
    for cue in result:
        item=cue["recommendation"]
        html.append("<article><h2>"+escape(str(cue["start"])+"–"+str(cue["end"])+"秒 | "+cue["intent"])+"</h2>")
        if item:
            html.append("<p>"+escape(item["title"])+"</p><p>仮スコア："+str(item["score"])+"</p><a href='"+escape(item["url"],quote=True)+"'>候補映像を確認</a><p><small>"+escape(" / ".join(item["issues"]) or "No automatic warning; manual review still mandatory")+"</small></p>")
        else:
            html.append("<p>候補なし。追加検索が必要。</p>")
        html.append("</article>")
    html.append("</html>")
    (out/"v09_storyboard.html").write_text("".join(html),encoding="utf-8")
    print(json.dumps({"cues":len(result),"license_cleared_cues":sum(x["recommendation"] is not None for x in result),"visual_approved":0,"timing_approved":0},ensure_ascii=False))
if __name__=="__main__":main()
