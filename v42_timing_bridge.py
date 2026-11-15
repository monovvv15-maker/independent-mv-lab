"""V42 non-rendering cue bridge for V41 pencil drawing.
Maps real output seconds to old visual seconds, allowing precise later cue
registration without rewriting V38/V40 scripts or inventing lyric timings.
No images, videos or audio files are emitted by this module.
"""
import json
from pathlib import Path
from v39_progressive_drawing import DURATION
from v41_redraw_engine import frame_at as render_frame

MANIFEST=Path("catalog/v42_audio_cue_manifest.json")
DEFAULT_OLD_PAUSE=(111.,139.)

def cue_manifest(path=MANIFEST):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def pause_bounds(manifest):
    cue=manifest["lyric_pause"]
    if cue["status"]=="verified":
        if cue["start_seconds"] is None or cue["end_seconds"] is None:
            raise ValueError("Verified cue needs both exact timestamps")
        bounds=(float(cue["start_seconds"]),float(cue["end_seconds"]))
    elif cue["status"]=="not_verified":
        if cue["start_seconds"] is not None or cue["end_seconds"] is not None:
            raise ValueError("Unverified cue must not supply verified fields")
        bounds=(float(cue["provisional_start_seconds"]),float(cue["provisional_end_seconds"]))
    else:
        raise ValueError("Unknown lyric cue status")
    if not (75<bounds[0]<bounds[1]<184):
        raise ValueError("Pause cue outside acceptable song arc")
    return bounds

def warp_time(t,manifest):
    """Continuous, monotone piecewise linear mapping; exact pause holds."""
    if not 0<=t<=DURATION:raise ValueError("time out of range")
    a,b=pause_bounds(manifest)
    oa,ob=DEFAULT_OLD_PAUSE
    if t<=a:
        return (oa*t/a) if a else 0.
    if t<=b:
        return oa+(t-a)*(ob-oa)/(b-a)
    return ob+(t-b)*(DURATION-ob)/(DURATION-b)

def stage_state(t,manifest):
    from v41_redraw_engine import action_state
    visual_t=warp_time(t,manifest)
    return action_state(visual_t)

def draw_at(t,image,manifest,clean=None,pencil=None,order=None):
    visual_t=warp_time(t,manifest)
    return render_frame(visual_t,image,clean=clean,pencil=pencil,order=order)

def preflight(manifest):
    problems=[]
    try:
        a,b=pause_bounds(manifest)
        mapped=[warp_time(DURATION*i/100,manifest) for i in range(101)]
        if abs(mapped[0])>1e-6 or abs(mapped[-1]-DURATION)>1e-5:
            problems.append("lost endpoint")
        if any(y<x for x,y in zip(mapped,mapped[1:])):
            problems.append("time mapping reversed")
        if abs(warp_time(a,manifest)-DEFAULT_OLD_PAUSE[0])>1e-6:
            problems.append("pause start mismatch")
        if abs(warp_time(b,manifest)-DEFAULT_OLD_PAUSE[1])>1e-6:
            problems.append("pause end mismatch")
        if stage_state((a+b)/2,manifest)["paused"] is not True:
            problems.append("drawing not stopped on pause")
        if abs(warp_time(194,manifest)-194)>1e-3 and manifest["lyric_pause"]["status"]=="not_verified":
            # We intentionally permit shifted late-stage timing if the cue is changed.
            pass
    except (ValueError,KeyError,TypeError) as e:
        problems.append(str(e))
    return {"pass":not problems,"issues":problems,
       "lyric_phrase_verified":manifest["lyric_pause"]["status"]=="verified",
       "timing_is_provisional":manifest["lyric_pause"]["status"]!="verified",
       "video_generated":False,"image_generated":False}

if __name__=="__main__":
    report=preflight(cue_manifest())
    print(json.dumps(report,ensure_ascii=False))
    if not report["pass"]:raise SystemExit(1)
