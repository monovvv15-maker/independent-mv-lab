"""V35 experimental motion-change analyzer for existing walking footage.
This does NOT decide whether a person stops: low frame-change may mean static camera.
Generates metadata only; no rendered or released images/videos.
"""
import json,subprocess
from pathlib import Path
from v18_pexels_review import get_video
from v28_full_renderer import ffmpeg_bin
FOOTAGE=[
(4464905,"person-walking-on-concrete-floor"),
(3998656,"close-up-shot-of-a-man-walking"),
(8729574,"point-of-view-of-a-person-walking-on-the-street")
]
W,H,FPS=64,36,3
def frame_change(a,b):
    if not a or len(a)!=len(b):raise ValueError("frame mismatch")
    return sum(abs(x-y) for x,y in zip(a,b))/(255*len(a))
def frames(movie,ffmpeg):
    cmd=[ffmpeg,"-hide_banner","-nostdin","-loglevel","error","-i",str(movie),
         "-vf",f"fps={FPS},scale={W}:{H},format=gray",
         "-f","rawvideo","-pix_fmt","gray","-"]
    process=subprocess.run(cmd,capture_output=True,timeout=150,check=True)
    b=process.stdout
    block=W*H
    return [b[i:i+block] for i in range(0,len(b)-block+1,block)]
def score(frames):
    deltas=[frame_change(x,y) for x,y in zip(frames,frames[1:])]
    if not deltas:return {"motion_sample_count":0,"median_change":None,"quiet_window_centers":[]}
    sorted_d=sorted(deltas)
    med=sorted_d[len(sorted_d)//2]
    # Quiet frames are relative to this clip. These are NOT verified stops.
    threshold=min(.04,max(.005,med*.45))
    windows=[]
    for k in range(len(deltas)-2):
        triple=deltas[k:k+3]
        if all(z<threshold for z in triple):
            windows.append(round((k+1.5)/FPS,2))
    return {"motion_sample_count":len(deltas),"median_change":round(med,5),
      "quiet_threshold":round(threshold,5),"quiet_window_centers":windows[:20],
      "note":"low pixel change != foot stop; requires full-motion review"}
def main():
    ffmpeg=ffmpeg_bin();rows=[]
    for id,slug in FOOTAGE:
        page=f"https://www.pexels.com/video/{slug}-{id}/"
        clip=Path(f"/tmp/v35_motion_{id}.mp4")
        entry={"id":id,"source_url":page,"visual_approved":False}
        try:
            get_video({"page":page,"download":f"https://www.pexels.com/download/video/{id}/"},clip)
            entry.update(score(frames(clip,ffmpeg)))
            entry["status"]="analyzed"
        except Exception as e:
            entry["status"]="failed";entry["error"]=type(e).__name__+":"+str(e)[:150]
        finally:clip.unlink(missing_ok=True)
        rows.append(entry)
    Path("discovery_output").mkdir(exist_ok=True)
    Path("discovery_output/v35_motion_screen.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False))
    print(json.dumps([{"id":x["id"],"status":x["status"],"windows":len(x.get("quiet_window_centers",[]))} for x in rows]))
if __name__=="__main__":main()
