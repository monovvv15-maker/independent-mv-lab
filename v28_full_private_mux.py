"""Private audio mux for full-song V28, 199.872s.
Never publishes or uploads a private MP3; only run after explicit video start.
"""
import argparse, hashlib, json, subprocess, shutil
from pathlib import Path
EXPECTED_SHA='d6615b1116569d603e2e630db9b08da0b065cd8208f877bb04c1d3ad63057764'
DURATION=199.872
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()
def cmd(ffmpeg,silent,audio,out):
    return [ffmpeg,'-hide_banner','-nostdin','-y','-i',str(silent),'-i',str(audio),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k',
            '-t',str(DURATION),'-movflags','+faststart',str(out)]
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--video',required=True)
    p.add_argument('--private-audio',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--authorize-render',action='store_true')
    a=p.parse_args()
    if not a.authorize_render:raise SystemExit('Video rendering has not been authorized')
    vid=Path(a.video);audio=Path(a.private_audio)
    if not vid.is_file() or not audio.is_file():raise FileNotFoundError('Input file missing')
    if sha(audio)!=EXPECTED_SHA:raise ValueError('Original song SHA mismatch')
    exe=shutil.which('ffmpeg')
    if not exe:raise RuntimeError('ffmpeg missing')
    subprocess.run(cmd(exe,vid,audio,Path(a.output)),check=True,timeout=300)
    print(json.dumps({'audio_muxed_locally':True,'uploaded_music':False,'expected_duration':DURATION}))
if __name__=='__main__':main()
