"""V20 private listener-confirmed lyric-cue validation.
No audio in public GitHub; never infer voice timings from RMS.
"""
import json
from pathlib import Path
KEYS=("first_vocal","shoes_word","rain_word")
def validate_marks(data):
    errors=[]
    if data.get("status")!="listener_review":
        errors.append("not listener reviewed")
    marks=data.get("marks",{})
    if not isinstance(marks,dict):return ["marks missing"]
    for key in KEYS:
        v=marks.get(key)
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not 0<=v<30:
            errors.append(key+": absent or outside 0..30 seconds")
    if not errors:
        if not (marks["first_vocal"]<=marks["shoes_word"]<=marks["rain_word"]):
            errors.append("chronology of first vocal, shoes and rain invalid")
    return errors
def main():
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    template={"status":"unverified","marks":{"first_vocal":None,"shoes_word":None,"rain_word":None},"song_sha256":"d6615b1116569d603e2e630db9b08da0b065cd8208f877bb04c1d3ad63057764"}
    (out/"v20_sync_template.json").write_text(json.dumps(template,ensure_ascii=False,indent=2),encoding="utf-8")
    errors=validate_marks(template)
    print(json.dumps({"sync_ready":not errors,"video_generated":False,"missing":errors},ensure_ascii=False))
if __name__=="__main__":main()
