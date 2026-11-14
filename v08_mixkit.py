"""V08 Mixkit license audit. No videos downloaded, no paywall bypass.
Results: verified_free / restricted / unverified. Unverified never passes gate.
"""
import json, re, urllib.request
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlparse

FREE_TEXT = "under the Mixkit Stock Video Free License"
RESTRICTED_TEXT = ("under the Mixkit Restricted License", "Free Download - 720p Version for Personal Use only")
def classify(text):
    normalized = unescape(re.sub(r"<[^>]+>", " ", text))
    normalized = re.sub(r"\s+", " ", normalized).lower()
    if any(s.lower() in normalized for s in RESTRICTED_TEXT):
        return "restricted"
    if FREE_TEXT.lower() in normalized and "for commercial or personal use" in normalized:
        return "verified_free"
    return "unverified"

def fetch_page(url, opener=None):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname!="mixkit.co" or not p.path.startswith("/free-stock-video/"):
        raise ValueError("only official Mixkit clip pages accepted")
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 IndependentMVLab/0.8"})
    if opener is None:opener=urllib.request.urlopen
    with opener(req,timeout=20) as res:
        return res.read(1024*1024).decode("utf-8","replace")

def audit(rows, fetcher=fetch_page):
    result=[]
    for item in rows:
        row=dict(item)
        try:
            actual=classify(fetcher(row["url"]))
            row["live_license"]=actual
            row["license_check"]="verified" if actual!="unverified" else "unknown"
        except Exception as exc:
            row["live_license"]="unverified"
            row["license_check"]="connection_failed"
            row["error"]=type(exc).__name__+": "+str(exc)[:100]
        row["eligible"]=row["expected_license"]=="free" and row["live_license"]=="verified_free"
        row["visual_review"]="pending"
        result.append(row)
    return result

def render(rows,path):
    cards=[]
    for r in rows:
        state="PASS LICENSE ONLY" if r["eligible"] else "NOT CLEARED"
        cards.append("<article><h3>"+escape(r["scene"]+" — "+r["title"])+"</h3><p>"+escape(state+" / "+r["live_license"])+"</p><p>"+escape(str(r["duration"])+"s | "+r["note"])+"</p><a target='_blank' rel='noopener noreferrer' href='"+escape(r["url"],quote=True)+"'>元動画を確認</a></article>")
    html="<html lang='ja'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{font:16px system-ui;background:#171717;color:white;padding:14px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}article{background:#282828;border-radius:10px;padding:12px}a{color:#add9ff}</style><h1>V08 Mixkit 実写素材候補</h1><p>権利検査と映像の目視検査は別。リンクから実動画を確認すること。</p><main>"+"".join(cards)+"</main></html>"
    Path(path).write_text(html,encoding="utf-8")

def main():
    folder=Path("discovery_output");folder.mkdir(exist_ok=True)
    rows=json.loads(Path("v08_mixkit_candidates.json").read_text())
    checked=audit(rows)
    (folder/"v08_license_audit.json").write_text(json.dumps(checked,ensure_ascii=False,indent=2),encoding="utf-8")
    render(checked,folder/"v08_review.html")
    scenes=sorted({r["scene"] for r in checked if r["eligible"]})
    print(json.dumps({"total":len(checked),"license_verified":sum(r["eligible"] for r in checked),"restricted":sum(r["live_license"]=="restricted" for r in checked),"unverified":sum(r["live_license"]=="unverified" for r in checked),"scene_coverage_license_only":len(scenes),"visual_review":"pending"},ensure_ascii=False))
    if not scenes:raise SystemExit("No video license verified; refuse adoption")
if __name__=="__main__":main()
