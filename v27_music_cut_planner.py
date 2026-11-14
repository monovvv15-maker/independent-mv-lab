"""V27 full-song cut decision: measured private-song transient/beat timing
plus V26 tag-based footage selection. Provisional until actual listening review.
No song waveform or MP3 stored in repository. No video generated.
"""
import json
from pathlib import Path
from v26_editorial_planner import CHAPTERS,score
CUT_ENDS=[6.048,11.904,17.792,23.648,30,36.064,41.92,47.808,53.664,59.552,65,71.264,77.152,83.008,88.896,94.752,99,105.184,111.008,116.928,122.784,128.672,134,139.776,145.632,151.488,157.376,163.232,168,173.664,179.552,185.44,191.264,199.872]
SONG_SHA256="d6615b1116569d603e2e630db9b08da0b065cd8208f877bb04c1d3ad63057764"
BPM_ESTIMATE=93.75
def plan(catalog,ends=CUT_ENDS):
    result=[];previous=None;used={};last=0
    for end in ends:
        midpoint=(last+end)/2
        idx=next((i for i,(a,b,_) in enumerate(CHAPTERS) if a<=midpoint<b),len(CHAPTERS)-1)
        prefs=CHAPTERS[idx][2]
        eligible=[c for c in catalog if
          c.get('duration') is not None and c['duration']>=end-last-0.05 and
          c.get('license_page')=='Free' and
          any(prefs.get(t,0)>0 for t in c.get('tags',[])) and
          not (c.get('width') and c.get('height') and c['width']<c['height'])]
        if not eligible:raise ValueError(f"No duration-eligible footage for {last:.3f}-{end:.3f}")
        choice=sorted(eligible,key=lambda c:(-score(c,prefs,previous,used),c['id']))[0]
        result.append({'start':round(last,3),'end':end,'chapter':idx+1,
          'clip_id':choice['id'],'source_url':choice['url'],'selection_method':'tags + repeat penalty',
          'cut_time_method':'measured beat/transient nearest 6s, chapter-boundary anchor',
          'visual_review':'pending','lyric_sync':'pending','render_authorized':False})
        previous=choice['id'];used[choice['id']]=used.get(choice['id'],0)+1;last=end
    return result
def validate(shots):
    errors=[];last=0.
    for s in shots:
        if abs(s['start']-last)>0.002:errors.append('gap')
        if s['end']<=s['start']:errors.append('invalid')
        last=s['end']
    if abs(last-199.872)>0.002:errors.append('duration')
    return errors
if __name__=='__main__':
    out=Path('discovery_output');out.mkdir(exist_ok=True)
    catalog=json.loads(Path('catalog/v26_full_length_candidates.json').read_text())['items']
    shots=plan(catalog)
    report={'source_audio_sha256':SONG_SHA256,'estimated_bpm':BPM_ESTIMATE,'cuts':len(shots),
      'unique_clips':len({s['clip_id'] for s in shots}),'errors':validate(shots),
      'ready_for_render':False,'actual_lyric_onsets_verified':False,'video_generated':False,'shots':shots}
    (out/'v27_music_timed_selection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='shots'},ensure_ascii=False))
    if report['errors']:raise SystemExit(1)
