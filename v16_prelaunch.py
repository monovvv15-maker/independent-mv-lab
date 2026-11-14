"""V16 single source of truth for pre-render readiness, no rendering."""
import json
from pathlib import Path

SONG_SHA256 = "d6615b1116569d603e2e630db9b08da0b065cd8208f877bb04c1d3ad63057764"
SONG_DURATION = 199.872
CLIPS = [
 {"scene":"01_intro","candidate":"mixkit-1","role":"morning atmosphere","status":"preview_only"},
 {"scene":"02_rain","candidate":"mixkit-4","role":"puddle on walking street","status":"preview_only"},
 {"scene":"03_shoe","candidate":"pexels-4953053","role":"putting on shoes","status":"page_metadata_only"},
 {"scene":"04_walk","candidate":"mixkit-7","role":"footsteps at crosswalk","status":"preview_only"},
 {"scene":"05_window","candidate":"mixkit-8","role":"opening a window","status":"preview_only"},
 {"scene":"06_neighborhood","candidate":None,"role":"sunlit residential street","status":"missing"},
]
def readiness(clips=CLIPS, voice_start_seconds=None, private_audio_present=False, full_clips_present=False, frame_review_complete=False):
    blockers=[]
    if not private_audio_present: blockers.append("private audio is not available inside the video-render environment")
    if voice_start_seconds is None: blockers.append("actual first sung syllable timestamp has not been verified by listening")
    if not full_clips_present: blockers.append("full source videos are not staged in the render environment")
    if not frame_review_complete: blockers.append("motion and crop review for final clip set not completed")
    for x in clips:
        if not x["candidate"]:blockers.append(x["scene"]+": no selected footage")
    return {"ready":not blockers,"mode":"pre_render_only","video_generated":False,"blockers":blockers,"song_duration_seconds":SONG_DURATION,"song_sha256":SONG_SHA256,"scenes":clips}
def main():
    out=Path("discovery_output");out.mkdir(exist_ok=True)
    r=readiness()
    (out/"v16_prelaunch.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"ready":r["ready"],"video_generated":False,"blocking_items":len(r["blockers"])},ensure_ascii=False))
if __name__=="__main__":main()
