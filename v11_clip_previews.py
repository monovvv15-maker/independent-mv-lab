"""V11: discover only explicitly exposed Mixkit public video previews and sample frames.
Never guess CDN URLs, authenticate, bypass download controls or distribute source clips.
"""
import json,re,html,urllib.request,subprocess
from pathlib import Path
from urllib.parse import urlparse, urljoin
from v08_mixkit import fetch_page

MAX_PREVIEW_BYTES=12*1024*1024
ALLOWED={"mixkit.co","static.mixkit.co","assets.mixkit.co"}

def find_preview_urls(page,base):
    # Accept ONLY links actually present in source HTML.
    decoded=html.unescape(page).replace("\\/","/")
    matches=re.findall(r'https?://[^\s"<>\\]+?\.mp4(?:\?[^\s"<>\\]*)?',decoded,re.I)
    matches+=re.findall(r'(?:src|content)=["\']([^"\']+\.mp4(?:\?[^"\']*)?)["\']',decoded,re.I)
    out=[]
    for url in matches:
        url=urljoin(base,url)
        p=urlparse(url)
        if p.scheme=="https" and p.hostname in ALLOWED and url not in out:
            out.append(url)
    return out

def take_still(url,path):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in ALLOWED:raise ValueError("untrusted preview host")
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 IndependentMVLab/1.1"})
    temp=path.with_suffix(".mp4")
    try:
        with urllib.request.urlopen(req,timeout=15) as resp,open(temp,"wb") as dst:
            length=resp.headers.get("Content-Length")
            if length and int(length)>MAX_PREVIEW_BYTES:raise ValueError("preview size limit")
            size=0
            while True:
                chunk=resp.read(262144)
                if not chunk:break
                size+=len(chunk)
                if size>MAX_PREVIEW_BYTES:raise ValueError("preview exceeds 12MB")
                dst.write(chunk)
        ffmpeg=__import__("imageio_ffmpeg").get_ffmpeg_exe()
        subprocess.run([ffmpeg,"-nostdin","-v","error","-ss","1","-i",str(temp),"-vf","scale=640:-2","-frames:v","1","-y",str(path)],timeout=30,check=True)
        if not path.exists():raise RuntimeError("frame missing")
    finally:
        temp.unlink(missing_ok=True)

def main():
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    clips=json.loads((out/"v08_license_audit.json").read_text(encoding="utf-8"))
    frames=out/"v11_frames";frames.mkdir(exist_ok=True)
    report=[]
    for clip in clips:
        if not clip.get("eligible"):continue
        row={"id":clip["id"],"scene":clip["scene"],"source":clip["url"],"status":"preview_unavailable","frame":None}
        try:
            page=fetch_page(clip["url"])
            urls=find_preview_urls(page,clip["url"])
            row["exposed_preview_count"]=len(urls)
            if urls:
                frame=frames/(clip["id"]+".jpg")
                take_still(urls[0],frame)
                row["status"]="frame_obtained"
                row["frame"]=str(frame.relative_to(out))
        except Exception as exc:
            row["error"]=type(exc).__name__+": "+str(exc)[:160]
        report.append(row)
    (out/"v11_preview_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    import html as h
    cards=[]
    for r in report:
        img='<img src="'+h.escape(r["frame"],quote=True)+'">' if r["frame"] else "<p>No still</p>"
        cards.append("<article>"+img+"<p>"+h.escape(r["scene"]+" "+r["id"]+" "+r["status"])+"</p><a href='"+h.escape(r["source"],quote=True)+"'>Official clip page</a></article>")
    (out/"v11_review.html").write_text("<!doctype html><html lang='ja'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{background:#111;color:#eee;font:16px system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}article{background:#222;padding:10px}img{width:100%}a{color:#9ce}</style><h1>V11 Preview Frames</h1><p>Source footage is not approved for the MV until visual and song review.</p><main>"+"".join(cards)+"</main></html>",encoding="utf-8")
    print(json.dumps({"eligible_clips":len(report),"frames_obtained":sum(r["status"]=="frame_obtained" for r in report),"no_preview":sum(r["status"]!="frame_obtained" for r in report)},ensure_ascii=False))
if __name__=="__main__":main()
