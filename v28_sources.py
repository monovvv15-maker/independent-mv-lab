"""V28 pre-render inspection of every UNIQUE clip picked by V27.
No music uploads and absolutely no final MP4 generation.
Caches only textual hashes + 3 small stills per clip in short-lived Artifacts.
"""
import json, subprocess
from pathlib import Path
from v27_music_cut_planner import plan,validate
from v18_pexels_review import get_video,frames

def selected(catalog):
    shots=plan(catalog)
    errors=validate(shots)
    if errors:raise ValueError(errors)
    ids={s['clip_id'] for s in shots}
    return [row for row in catalog if row['id'] in ids],shots

def inspect(catalog,root,fetch=get_video,extract=frames):
    chosen, shots=selected(catalog)
    root.mkdir(parents=True,exist_ok=True)
    stills=root/'stills';stills.mkdir(exist_ok=True)
    report=[]
    for row in chosen:
        movie=root/(str(row['id'])+'.mp4')
        item={'id':row['id'],'source_url':row['url'],'tags':row['tags'],
              'licensing':'provider listing only, recheck before publication',
              'status':'missing','visual_approval':False}
        try:
            details=fetch({'download':row['download_url'],'page':row['url']},movie)
            item.update(details)
            item['stills']=extract(movie,stills,str(row['id']))
            item['status']='preview_ready'
        except Exception as e:
            item['error']=type(e).__name__+': '+str(e)[:150]
        finally:
            movie.unlink(missing_ok=True)
        report.append(item)
    result={'song_duration':199.872,'shot_count':len(shots),'selected_unique':len(chosen),
            'preview_ready':sum(r['status']=='preview_ready' for r in report),
            'unavailable':[r['id'] for r in report if r['status']!='preview_ready'],
            'full_motion_review':'pending','video_rendered':False,'clips':report}
    (root/'report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return result

def main():
    catalog=json.loads(Path('catalog/v26_full_length_candidates.json').read_text(encoding='utf-8'))['items']
    result=inspect(catalog,Path('v28_review'))
    print(json.dumps({key:result[key] for key in ('selected_unique','preview_ready','unavailable','shot_count','video_rendered')},ensure_ascii=False))
    if result['preview_ready']<max(4,result['selected_unique']-3):
        raise SystemExit('Too many selected source videos unavailable; reject full render until replaced.')
if __name__=='__main__':main()
