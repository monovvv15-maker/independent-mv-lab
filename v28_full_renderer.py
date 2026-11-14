"""V28 full 199.872-second silent rough renderer, manual-only.
Privacy: never uploads music. Runs only with explicit --authorize-render.
Memory-conscious: renders each shot to an identical 720p H.264 segment,
then stream-concats. Download caches live only in temporary directories.

This is a PROVISIONAL rough: beat candidates, not verified lyric timestamps.
"""
import argparse,json,hashlib,re,subprocess,tempfile
from pathlib import Path
from v27_music_cut_planner import plan,validate
from v28_final_prelaunch import run as check_prelaunch
from v18_pexels_review import get_video

SONG_DURATION=199.872
def cutplan(catalog):
    cuts=plan(catalog)
    if validate(cuts):raise ValueError('invalid cut plan')
    return cuts

def ffmpeg_bin():
    return __import__('imageio_ffmpeg').get_ffmpeg_exe()

def duration_of(path,ffmpeg):
    proc=subprocess.run([ffmpeg,'-hide_banner','-i',str(path)],capture_output=True,text=True,timeout=25)
    m=re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)',proc.stderr)
    if not m:raise ValueError('Cannot probe movie duration')
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))

def trim_command(ffmpeg,source,out,source_start,seconds):
    # Letterbox (no stretched persons). Rescale down only: 720p target.
    vf='scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p'
    return [ffmpeg,'-hide_banner','-nostdin','-loglevel','error','-y','-ss',f'{source_start:.3f}',
            '-i',str(source),'-t',f'{seconds:.3f}','-an','-vf',vf,
            '-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',
            '-r','30','-pix_fmt','yuv420p','-video_track_timescale','30000',
            str(out)]

def concat_command(ffmpeg,manifest,out):
    return [ffmpeg,'-hide_banner','-nostdin','-loglevel','error','-y','-f','concat','-safe','0',
            '-i',str(manifest),'-c','copy','-movflags','+faststart',str(out)]

def source_offset(index,src_duration,clip_duration):
    # Keep 0.5s of safety room so next clip won't run out of source frames.
    avail=max(0,src_duration-clip_duration-0.5)
    return min(avail,(index%4)*2.25)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--authorize-render',action='store_true')
    p.add_argument('--output',default='v28_full_silent_rough.mp4')
    p.add_argument('--catalog',default='catalog/v26_full_length_candidates.json')
    args=p.parse_args()
    if not args.authorize_render:raise SystemExit('Must have explicit 動画生成開始 approval')
    catalog=json.loads(Path(args.catalog).read_text(encoding='utf-8'))['items']
    gate=check_prelaunch(catalog)
    if not gate['technical_preflight_pass']:
        raise ValueError('Source QA incomplete: '+str(gate['errors']))
    cuts=cutplan(catalog)
    by_id={x['id']:x for x in catalog}
    ffmpeg=ffmpeg_bin()
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        sources={};lengths={}
        for i in sorted({c['clip_id'] for c in cuts}):
            row=by_id[i];dst=tmp/(str(i)+'.mp4')
            get_video({'download':row['download_url'],'page':row['url']},dst)
            length=duration_of(dst,ffmpeg)
            max_cut=max(s['end']-s['start'] for s in cuts if s['clip_id']==i)
            if length<max_cut-0.1:raise ValueError(f'Clip {i} too short')
            sources[i]=dst;lengths[i]=length
        segs=tmp/'segs';segs.mkdir()
        names=[]
        occurrences={}
        for k,cut in enumerate(cuts):
            ident=cut['clip_id'];sec=cut['end']-cut['start']
            used=occurrences.get(ident,0);occurrences[ident]=used+1
            pos=source_offset(used,lengths[ident],sec)
            dst=segs/(f'{k:03d}.mp4')
            subprocess.run(trim_command(ffmpeg,sources[ident],dst,pos,sec),check=True,timeout=100)
            if not dst.is_file() or dst.stat().st_size<1000:raise RuntimeError(f'Bad segment {k}')
            names.append(dst)
        playlist=tmp/'concat.txt'
        playlist.write_text(''.join("file '"+str(x)+"'\n" for x in names),encoding='utf-8')
        output=Path(args.output).resolve()
        subprocess.run(concat_command(ffmpeg,playlist,output),check=True,timeout=120)
        if output.stat().st_size<10000:raise RuntimeError('Bad final MP4')
    print(json.dumps({'generated':True,'audio_included':False,'rough_only':True,'cuts':len(cuts),
                      'unique_sources':len(sources),'size_bytes':output.stat().st_size},ensure_ascii=False))
if __name__=='__main__':main()
