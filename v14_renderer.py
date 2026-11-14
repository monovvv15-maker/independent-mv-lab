"""V14 deterministic local renderer. Does not run on push or auto-download.

Only run after an explicit video-generation request and human footage approval.
Uses ffmpeg on an existing audio file and locally authorized video files.
"""
import argparse,json,subprocess,shutil
from pathlib import Path
from v13_edl import check_edl

def commands(edl,audio,output):
    blockers=check_edl(edl)
    if blockers:raise ValueError("Rendering blocked: "+"; ".join(blockers))
    if not audio.is_file():raise FileNotFoundError("Audio is missing: "+str(audio))
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg:raise FileNotFoundError("FFmpeg not installed")
    inputs=[]
    vf=[]
    for i,shot in enumerate(sorted(edl,key=lambda a:a["start"])):
        p=Path(shot["local_video"])
        if not p.is_file():raise FileNotFoundError("Footage missing: "+str(p))
        inputs+=["-i",str(p)]
        seconds=float(shot["end"])-float(shot["start"])
        # No upscaling inference or extra AI imagery. Only real footage.
        vf.append(f"[{i}:v]trim=duration={seconds:.3f},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p[v{i}]")
    vf.append("".join(f"[v{i}]" for i in range(len(edl)))+f"concat=n={len(edl)}:v=1:a=0[v]")
    cmd=[ffmpeg,"-hide_banner","-y",*inputs,"-i",str(audio),"-filter_complex",";".join(vf),"-map","[v]","-map",f"{len(edl)}:a:0","-t","30","-c:v","libx264","-preset","medium","-crf","19","-r","30","-c:a","aac","-b:a","192k","-movflags","+faststart",str(output)]
    return cmd

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--edl",required=True)
    p.add_argument("--audio",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--dry-run",action="store_true")
    args=p.parse_args()
    items=json.loads(Path(args.edl).read_text(encoding="utf-8"))
    cmd=commands(items,Path(args.audio),Path(args.output))
    if args.dry_run:
        print(json.dumps({"video_generated":False,"command":cmd},ensure_ascii=False))
        return
    subprocess.run(cmd,check=True,timeout=900)
    print(json.dumps({"video_generated":True,"output":args.output},ensure_ascii=False))
if __name__=="__main__":main()
