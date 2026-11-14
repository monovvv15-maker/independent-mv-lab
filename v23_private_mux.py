"""Private audio muxing after explicit generation instruction. Never uploads MP3 to GitHub."""
import argparse,hashlib,json,subprocess,shutil
from pathlib import Path
def sha256(path):
 digest=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
 return digest.hexdigest()
def command(ffmpeg,silent_mp4,private_mp3,output):
 return [ffmpeg,'-hide_banner','-nostdin','-y','-i',str(silent_mp4),'-i',str(private_mp3),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(output)]
def main():
 p=argparse.ArgumentParser()
 for arg in ('silent-video','private-mp3','expected-sha256','output'):p.add_argument('--'+arg,required=True)
 p.add_argument('--authorize-render',action='store_true')
 args=p.parse_args()
 if not args.authorize_render:raise SystemExit('Author must say 動画生成開始')
 silent=Path(args.silent_video);song=Path(args.private_mp3);out=Path(args.output)
 if not silent.is_file() or not song.is_file():raise FileNotFoundError('Source missing')
 if sha256(song)!=args.expected_sha256:raise ValueError('Song SHA mismatch')
 exe=shutil.which('ffmpeg')
 if not exe:raise FileNotFoundError('ffmpeg missing')
 subprocess.run(command(exe,silent,song,out),check=True,timeout=180)
 if out.stat().st_size<10000:raise RuntimeError('Invalid MP4')
 print(json.dumps({'mux_finished':True,'private_audio_uploaded':False,'size_bytes':out.stat().st_size}))
if __name__=='__main__':main()
