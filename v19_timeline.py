"""V19: build a lyric-aware shot timeline without guessing vocals.
No audio or video is created, downloaded, uploaded, or shared.
"""
import json
from pathlib import Path

def draft(first_vocal_sec=None):
    if first_vocal_sec is None:
        return {"render_ready":False,"reason":"first_vocal_sec is not listening-verified","cues":[
            {"role":"intro","start":0,"end":None,"status":"awaiting first_vocal_sec"},
            {"role":"shoes","start":None,"end":None,"status":"awaiting lyric timing"},
            {"role":"rain","start":None,"end":None,"status":"awaiting lyric timing"}]}
    v=float(first_vocal_sec)
    if not (2<=v<=28):raise ValueError("First vocal must lie within 2..28s")
    return {"render_ready":False,"reason":"vocal start input alone does not verify words or footage","cues":[
        {"role":"intro","start":0.0,"end":v,"candidate":"residential_morning","time_basis":"vocal onset"},
        {"role":"shoes","start":v,"end":None,"candidate":"pexels-4953053","time_basis":"word timing not entered"},
        {"role":"rain","start":None,"end":30.0,"candidate":"mixkit-4","time_basis":"word timing not entered"}]}

def main():
    folder=Path("discovery_output");folder.mkdir(exist_ok=True)
    (folder/"v19_timeline_template.json").write_text(json.dumps(draft(),ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"v19_timeline_created":True,"video_generated":False,"song_onset_confirmed":False}))
if __name__=="__main__":main()
