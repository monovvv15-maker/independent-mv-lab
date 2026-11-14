"""V12 sync and casting quality gate. Never treat audio energy as lyric timestamps."""
from dataclasses import dataclass
@dataclass(frozen=True)
class ShotChoice:
    scene: str
    source_url: str
    license_ok: bool
    footage_reviewed: bool
    aspect_ok: bool
    chronology_ok: bool
    protagonist_ok: bool

def preflight(choices, lyric_timing_verified):
    reasons=[]
    if not lyric_timing_verified:
        reasons.append("Real-listening lyric timings are unverified; never position words from 5-second blocks")
    if not choices:
        reasons.append("No video shots approved")
    for item in choices:
        if not item.license_ok: reasons.append(item.scene+": license not verified")
        if not item.footage_reviewed: reasons.append(item.scene+": video motion/content not visually reviewed")
        if not item.aspect_ok: reasons.append(item.scene+": incompatible crop or aspect ratio")
        if not item.chronology_ok: reasons.append(item.scene+": lighting/time continuity mismatch")
        if not item.protagonist_ok: reasons.append(item.scene+": visible-person continuity mismatch")
    return {"ready":not reasons, "blockers":reasons}

if __name__ == "__main__":
    import json
    report=preflight([ShotChoice("shoe closeup","https://www.pexels.com/video/a-person-putting-on-a-shoe-8994347/",True,False,False,False,False)],False)
    print(json.dumps(report,ensure_ascii=False))
