"""V18: inspect two explicitly identified free Pexels clips.
No guessed CDN paths. Download follows the provider's public Free Download redirect.
Keep movie bytes temporary; publish only still review images and technical metadata.
"""
import json, hashlib, subprocess, urllib.request
from urllib.parse import urlparse
from pathlib import Path
MAX_BYTES = 100*1024*1024
VIDEOS = [
 {"id":"shoe","page":"https://www.pexels.com/video/low-angle-view-of-a-person-putting-on-the-shoe-and-tying-it-4953053/","download":"https://www.pexels.com/download/video/4953053/","expected_duration":9},
 {"id":"street","page":"https://www.pexels.com/video/quiet-urban-street-in-early-morning-light-29906907/","download":"https://www.pexels.com/download/video/29906907/","expected_duration":8},
]
ALLOWED = {"videos.pexels.com", "www.pexels.com", "pexels.com"}
def valid_final_url(url):
    p=urlparse(url)
    return p.scheme=="https" and p.hostname in {"videos.pexels.com"}
def get_video(item,destination,opener=None,cap=MAX_BYTES):
    request=urllib.request.Request(item["download"],headers={"User-Agent":"Mozilla/5.0 IndependentMVLab/1.8","Referer":item["page"]})
    opener=opener or urllib.request.urlopen
    digest=hashlib.sha256()
    with opener(request,timeout=40) as resp:
        if not valid_final_url(resp.geturl()):raise ValueError("download redirected outside official Pexels video CDN")
        size_header=resp.headers.get("Content-Length")
        if size_header and int(size_header)>cap:raise ValueError("media exceeds capped bytes")
        total=0
        with open(destination,"wb") as output:
            while True:
                part=resp.read(256*1024)
                if not part:break
                total+=len(part)
                if total>cap:raise ValueError("media exceeds capped bytes")
                digest.update(part);output.write(part)
    return {"bytes":total,"sha256":digest.hexdigest(),"final_url_host":"videos.pexels.com"}
def frames(movie,dirpath,clip_id):
    ffmpeg=__import__("imageio_ffmpeg").get_ffmpeg_exe()
    names=[]
    for sec in [0.3,2.0,4.5]:
        outfile=dirpath/(clip_id+"_"+str(sec).replace(".","_")+".jpg")
        command=[ffmpeg,"-nostdin","-hide_banner","-loglevel","error","-y","-ss",str(sec),"-i",str(movie),"-frames:v","1","-vf","scale=640:-2",str(outfile)]
        subprocess.run(command,check=True,timeout=40)
        if outfile.is_file() and outfile.stat().st_size>100:
            names.append(str(outfile.relative_to(dirpath.parent)))
    if len(names)<2:raise RuntimeError("insufficient valid frames")
    return names
def main():
    root=Path("v18_review");root.mkdir(exist_ok=True)
    img=root/"stills";img.mkdir(exist_ok=True)
    rows=[]
    for item in VIDEOS:
        temp=root/(item["id"]+".mp4")
        row={"id":item["id"],"page":item["page"],"visual_approval":False}
        try:
            info=get_video(item,temp)
            row.update(info)
            row["frames"]=frames(temp,img,item["id"])
            row["status"]="frames_extracted"
        except Exception as exc:
            row.update(status="unavailable",error=type(exc).__name__+": "+str(exc)[:210])
        finally:
            temp.unlink(missing_ok=True)
        rows.append(row)
    (root/"v18_report.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    from html import escape
    html=["<!doctype html><html lang='ja'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{font:16px system-ui;background:#171717;color:#eee;padding:16px}img{width:100%;max-width:560px}figure{display:inline-block;width:32%;min-width:210px;margin:4px}a{color:#bde0ff}</style><h1>V18 real Pexels frame inspection</h1><p>Downloaded clips deleted after inspection. Approval is still pending.</p>"]
    for r in rows:
        html.append("<h2>"+escape(r["id"]+" / "+r["status"])+"</h2><a href='"+escape(r["page"],quote=True)+"'>Original Pexels source</a>")
        for frame in r.get("frames",[]):
            html.append("<figure><img src='"+escape(frame,quote=True)+"'></figure>")
    (root/"index.html").write_text("".join(html)+"</html>",encoding="utf-8")
    print(json.dumps({"attempted":len(rows),"frames_extracted":sum(r["status"]=="frames_extracted" for r in rows),"original_videos_retained":0,"visual_approved":0}))
if __name__=="__main__":main()
