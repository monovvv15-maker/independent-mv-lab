"""V28 final no-render gate. All media must have proven retrievability in V28 QA.
The resulting file is a ready-to-render *technical* recipe, not artistic approval.
"""
import json
from pathlib import Path
from v27_music_cut_planner import plan, validate

def run(catalog):
    shots=plan(catalog)
    errors=validate(shots)
    rows={c['id']:c for c in catalog}
    selected=sorted({s['clip_id'] for s in shots})
    missing=[ident for ident in selected if rows[ident].get('retrieval_status')!='preview_frame_extracted']
    errors += [f'No verified source fetch for {ident}' for ident in missing]
    return {'cut_count':len(shots),'unique_footage':len(selected),'duration':199.872,
            'technical_preflight_pass':not errors,'quality_approved':False,
            'music_lyric_sync':'unverified','source_ids':selected,'errors':errors,
            'render_executed':False,'cuts':shots}

def main():
    catalog=json.loads(Path('catalog/v26_full_length_candidates.json').read_text())['items']
    result=run(catalog)
    out=Path('discovery_output');out.mkdir(exist_ok=True)
    (out/'v28_final_prelaunch.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in result.items() if k!='cuts'},ensure_ascii=False))
    if not result['technical_preflight_pass']:raise SystemExit(1)
if __name__=='__main__':main()
