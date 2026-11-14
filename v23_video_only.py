"""Manual-only video compositor. Never uses private audio or auto-runs on push."""
import argparse,json,subprocess,tempfile
from pathlib import Path
from v23_prelaunch import SHOTS,validate
def ffmpeg_command(files,output,encoder):
 if len(files)!=len(SHOTS) or validate():raise ValueError('shot count mismatch')
 chain=[]
 for i,(_,ident,_,sec) in enumerate(SHOTS):
  chain.append(f'[{i}:v]trim=start=0:duration={sec:.3f},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p[v{i}]')
 chain.append(''.join(f'[v{i}]' for i in range(len(SHOTS)))+f'concat=n={len(SHOTS)}:v=1:a=0[outv]')
 return [encoder,'-hide_banner','-nostdin','-y',*sum((['-i',str(p)] for p in files),[]),'-filter_complex',';'.join(chain),'-map','[outv]','-an','-t','30','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--authorize-render',action='store_true');args=p.parse_args()
 if not args.authorize_render:raise SystemExit('Explicit author confirmation required')
 from v18_pexels_review import get_video
 encoder=__import__('imageio_ffmpeg').get_ffmpeg_exe()
 output=Path(args.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  clips=[]
  for name,ident,url,sec in SHOTS:
   p=Path(td)/(name+'.mp4')
   get_video({'download':f'https://www.pexels.com/download/video/{ident}/','page':url},p)
   clips.append(p)
  subprocess.run(ffmpeg_command(clips,output,encoder),check=True,timeout=900)
 if not output.exists() or output.stat().st_size<2000:raise RuntimeError('missing video output')
 print(json.dumps({'video_generated':True,'original_music_uploaded':False,'audio_embedded':False,'file_size':output.stat().st_size}))
if __name__=='__main__':main()
