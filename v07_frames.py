"""V07 safe, bounded extraction from real Wikimedia videos.
Only Wikimedia-hosted HTTPS URLs; never trusts arbitrary catalog URLs.
"""
import json, subprocess, shutil, urllib.request
from pathlib import Path
from urllib.parse import urlparse
MAX_BYTES=28*1024*1024
MAX_ITEMS=8
def allowed(url):
    try:
        p=urlparse(url)
        return p.scheme=="https" and p.hostname in {"upload.wikimedia.org","upload.wikimedia.org"}
    except Exception:return False

def pull(url,destination,max_bytes=MAX_BYTES):
    if not allowed(url):raise ValueError("untrusted media URL")
    req=urllib.request.Request(url,headers={"User-Agent":"IndependentMVLab/0.7 (https://github.com/monovvv15-maker/independent-mv-lab)"})
    with urllib.request.urlopen(req,timeout=25) as inp, open(destination,"wb") as out:
        header=inp.headers.get("Content-Length")
        if header and int(header)>max_bytes:raise ValueError("video too large")
        count=0
        while True:
            chunk=inp.read(1024*256)
            if not chunk:break
            count+=len(chunk)
            if count>max_bytes:raise ValueError("video exceeds download cap")
            out.write(chunk)
    return count
def extract(path,output):
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-ss","1","-i",str(path),"-frames:v","1","-vf","scale=640:-2",str(output)],check=True,timeout=30)
    if not output.exists():raise RuntimeError("missing extracted frame")

def main():
    out=Path("discovery_output")
    data=json.loads((out/"v06_candidates.json").read_text(encoding="utf-8"))
    by_scene={}
    for item in data:
        by_scene.setdefault(item["scene_id"],[]).append(item)
    report=[]
    frames=out/"video_frames"
    frames.mkdir(exist_ok=True)
    tried=0
    for scene,items in by_scene.items():
        for item in items[:2]:
            if tried>=MAX_ITEMS:break
            tried+=1
            uri=item.get("download_url","")
            temp=frames/(item["id"]+".webm")
            img=frames/(item["id"]+".jpg")
            row={"scene":scene,"id":item["id"],"title":item["title"],"source":item["source_url"],"license":item["license"],"author":item.get("author","")}
            try:
                size=pull(uri,temp)
                extract(temp,img)
                row.update(status="extracted",bytes=size,frame=str(img.relative_to(out)))
            except Exception as exc:
                row.update(status="skipped",error=type(exc).__name__+": "+str(exc)[:170])
            finally:
                temp.unlink(missing_ok=True)
            report.append(row)
    (out/"v07_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    cards=[]
    from html import escape
    for r in report:
        frame=r.get("frame")
        img=f'<img src="{escape(frame,quote=True)}">' if frame else '<p>Frame not obtained</p>'
        cards.append('<article>'+img+'<p>'+escape(r["scene"]+" | "+r["status"]+" | "+r["title"])+'</p><a href="'+escape(r["source"],quote=True)+'">Source and license</a></article>')
    html='<!DOCTYPE html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#111;color:white;font:15px system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}article{background:#222;padding:10px}img{width:100%}a{color:#aef}</style><h1>V07 real-video frame inspection</h1><p>Manual visual review required before reuse. Metadata license is not a final rights clearance.</p><main>'+''.join(cards)+'</main></html>'
    (out/"v07_review.html").write_text(html,encoding="utf-8")
    print(json.dumps({"attempted":len(report),"extracted":sum(x["status"]=="extracted" for x in report),"skipped":sum(x["status"]!="extracted" for x in report)},ensure_ascii=False))
    # The workflow intentionally succeeds even if all large videos were skipped.
if __name__=="__main__":main()
