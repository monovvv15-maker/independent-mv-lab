"""V37 authorised music video: single use of each real footage source.

Creator approval: 2026-11-15 '動画生成開始'. This is a story rough, not final lyric
sync. No MP3 uploaded to GitHub. All original footage is ephemeral.
"""
import argparse,json,math,subprocess,tempfile
from pathlib import Path
from v18_pexels_review import get_video
from v28_full_renderer import ffmpeg_bin,duration_of,concat_command
from v31_style_engine import filter_chain

DURATION=199.872
PLAN=Path("catalog/v37_unique_sources_plan.json")
REJECT={5034328,6136988,3031954,37239481,4310191}
def validate(shots):
    ids=[s["id"] for s in shots]
    if len(set(ids))!=len(ids):raise ValueError("repeated real source forbidden")
    if set(ids)&REJECT:raise ValueError("rejected clip entered edit")
    if not shots or shots[0]["id"]!=4953053:raise ValueError("opening shoe lost")
    if len(shots)<20:raise ValueError("not enough visual variety")
    if len(set(s["grammar"] for s in shots))!=len(shots):
        raise ValueError("repeated shot grammar")
    if sum(s["weight"] for s in shots)<175:raise ValueError("insufficient source duration weights")
    return True

def assign(shots,real_durations):
    # Duration caps ensure each source appears once. Mild slowdown up to 12% only.
    capacities=[max(0,min(real_durations[s["id"]]-0.2,real_durations[s["id"]]*.985)*1.12) for s in shots]
    if any(x<3.25 for x in capacities):raise ValueError("unusable short stock source")
    if sum(capacities)<DURATION:raise ValueError(f"Not enough unique unlooped footage: {sum(capacities):.2f}s")
    durations=[0.]*len(shots);remaining=DURATION;active=set(range(len(shots)))
    while active and remaining>0.00001:
        weight=sum(shots[i]["weight"] for i in active)
        limits={i:max(0,capacities[i]-durations[i]) for i in active}
        deltas={i:min(limits[i],remaining*shots[i]["weight"]/weight) for i in active}
        allocation=sum(deltas.values())
        for i,n in deltas.items():durations[i]+=n
        remaining-=allocation
        active={i for i in active if capacities[i]-durations[i]>0.00001}
        if allocation<0.00001:break
    if remaining>0.003:raise ValueError("Cannot fill song without repeating footage")
    durations[-1]+=DURATION-sum(durations)
    if any(x<3 for x in durations):raise ValueError("too-short visual segment")
    return durations

def make_segment(exe,source,dst,output_seconds,available):
    input_sec=min(available-0.18,output_seconds)
    if input_sec<=0:raise ValueError("source duration invalid")
    speed=output_seconds/input_sec
    if speed>1.121:raise ValueError("footage would require excessive slow motion")
    vf=("setpts="+f"{speed:.7f}*(PTS-STARTPTS),"
        "scale=1280:720:force_original_aspect_ratio=decrease,"
        "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,"
        +filter_chain()+",fps=30,format=yuv420p")
    cmd=[exe,"-hide_banner","-nostdin","-loglevel","error","-y",
        "-i",str(source),"-t",f"{input_sec:.3f}","-an","-vf",vf,
        "-c:v","libx264","-preset","veryfast","-crf","27",
        "-threads","2","-pix_fmt","yuv420p","-video_track_timescale","30000",str(dst)]
    subprocess.run(cmd,check=True,timeout=130)
    if not dst.exists() or dst.stat().st_size<1000:raise RuntimeError("segment invalid")

def render(out):
    plan=json.loads(PLAN.read_text(encoding="utf-8"))
    allshots=plan["shots"];validate(allshots)
    exe=ffmpeg_bin()
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);items=[];fails=[]
        for shot in allshots:
            vid=root/(str(shot["id"])+".mp4")
            try:
                get_video({"download":shot["source_url"],"page":shot["source_url"]},vid)
                sec=duration_of(vid,exe)
                if sec<3.5:raise ValueError("source below 3.5 seconds")
                items.append((shot,vid,sec))
                print("FETCH_OK",shot["id"],f"{sec:.2f}s",flush=True)
            except Exception as e:
                fails.append((shot["id"],str(e)[:180]))
                vid.unlink(missing_ok=True)
                print("FETCH_FAILED",shot["id"],str(e)[:180],flush=True)
        if len(items)<22:raise RuntimeError("Too few different sources: "+str(fails))
        shots=[x[0] for x in items];validate(shots)
        lengths={x[0]["id"]:x[2] for x in items}
        durations=assign(shots,lengths)
        segments=root/"segments";segments.mkdir()
        paths=[]
        for i,((s,clip,real_sec),desired) in enumerate(zip(items,durations)):
            dest=segments/f"{i:03}.mp4"
            make_segment(exe,clip,dest,desired,real_sec)
            paths.append(dest)
            print("CUT",i,s["id"],round(desired,3),s["meaning"],flush=True)
        manifest=root/"concat.txt"
        manifest.write_text("".join("file '"+str(p)+"'\\n" for p in paths).replace("\\n","\n"),encoding="utf-8")
        subprocess.run(concat_command(exe,manifest,Path(out).resolve()),check=True,timeout=200)
        Path(str(out)+".qa.json").write_text(json.dumps({
          "duration_planned":DURATION,"unique_shots":len(paths),"source_ids":[s["id"] for s in shots],
          "source_failures":fails,"no_repeated_asset":True,"music_included":False,
          "lyric_word_sync_verified":False,"story_rough":True},ensure_ascii=False,indent=2))
    print("V37_COMPLETE",out,Path(out).stat().st_size,flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument("--authorized",action="store_true")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    if not a.authorized:raise SystemExit("Video-generation approval required")
    render(a.output)
if __name__=="__main__":main()
