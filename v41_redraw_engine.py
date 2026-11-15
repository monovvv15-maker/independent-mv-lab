"""V41 non-destructive hand-drawn imperfection layer for the V39 jacket engine.

All functions calculate frames in memory; importing/running this file does not
save images or create videos. The actual source jacket is only read privately
when a future authorized renderer is executed.

One locally mistaken road outline is sketched, erased, then redrawn; faint
erasure graphite remains until final photo completion.
"""
import json
import numpy as np
import cv2
from v39_progressive_drawing import frame_at as original_frame, DURATION

# Provisional scene timing, not word-level lyric alignment.
DRAFT_START=12.
HESITATE_START=38.
WRONG_LINE_START=43.
ERASE_START=53.
CORRECT_START=59.
REDRAW_END=71.
PAUSE_START=111.
PAUSE_END=139.
PHOTO_RESTORE_START=161.
PHOTO_FINISH=194.

# All positions are normalized to source frame, subject to actual-image visual QA.
# A SINGLE roadway edge near the lower right, away from title / rails.
WRONG_POINTS=((.58,.66),(.68,.78),(.80,.98))
CORRECT_POINTS=((.59,.66),(.72,.81),(.88,.98))
DRAFT_POINTS=((.40,.56),(.29,.74),(.15,.99))
PENCIL_COLOR=np.array([111,112,118],dtype=np.float32)  # BGR soft graphite

def ease(x):
    q=float(np.clip(x,0,1))
    return q*q*(3-2*q)

def stroke_mask(shape,points,width=2):
    h,w=shape[:2]
    coords=np.array([[round(x*(w-1)),round(y*(h-1))] for x,y in points],dtype=np.int32)
    layer=np.zeros((h,w),dtype=np.uint8)
    cv2.polylines(layer,[coords],False,255,thickness=max(1,round(width*w/720)),
                  lineType=cv2.LINE_AA)
    return layer.astype(np.float32)/255

def alpha_over(frame,mask,opacity):
    strength=mask[...,None]*float(np.clip(opacity,0,1))
    data=frame.astype(np.float32)*(1-strength)+PENCIL_COLOR[None,None,:]*strength
    return np.clip(data,0,255).astype(np.uint8)

def action_state(t):
    """Inspectable independent channels for exact one-off imperfection QA."""
    if t<0 or t>DURATION:raise ValueError("time outside music")
    # Draft starts faint, before the stronger main linework.
    draft=.0 if t<DRAFT_START else .21*ease((t-DRAFT_START)/23)
    if t>=75:draft*=1-ease((t-75)/15)
    # Mistaken road line only appears once, never cycles/repeats.
    wrong=0.
    if t>=WRONG_LINE_START:
        wrong=.40*ease((t-WRONG_LINE_START)/5)
        if t>=ERASE_START:
            wrong*=1-ease((t-ERASE_START)/6)
    # Ghost graphite begins when erasing starts and remains faint until photo.
    ghost=.0 if t<ERASE_START else .085*ease((t-ERASE_START)/6)
    # Corrected stroke is gradual and exists once.
    corrected=0. if t<CORRECT_START else .46*ease((t-CORRECT_START)/(REDRAW_END-CORRECT_START))
    if t>=PHOTO_RESTORE_START:
        fade=1-ease((t-PHOTO_RESTORE_START)/(PHOTO_FINISH-PHOTO_RESTORE_START))
        draft*=fade
        wrong*=fade
        ghost*=fade
        corrected*=fade
    return {"draft":draft,"wrong":wrong,"ghost":ghost,"corrected":corrected,
            "paused": PAUSE_START<=t<PAUSE_END}

def frame_at(t,im,clean=None,pencil=None,order=None):
    """One V39 frame plus bounded V40 pencil mistakes, no side effects."""
    base=original_frame(t,im,clean=clean,pencil=pencil,order=order)
    state=action_state(t)
    if not any(state[key] for key in ("draft","wrong","ghost","corrected")):
        return base
    # Draw order: paper draft -> residual erasure -> flawed line -> correction.
    m_draft=stroke_mask(base.shape,DRAFT_POINTS,2)
    m_wrong=stroke_mask(base.shape,WRONG_POINTS,2)
    m_correct=stroke_mask(base.shape,CORRECT_POINTS,2)
    out=alpha_over(base,m_draft,state["draft"])
    out=alpha_over(out,m_wrong,state["ghost"])
    out=alpha_over(out,m_wrong,state["wrong"])
    out=alpha_over(out,m_correct,state["corrected"])
    return out

def quality_gate():
    states=[action_state(x) for x in [0,20,45,51,56,65,100,115,135,150,194,DURATION]]
    issues=[]
    if any(states[0][k] for k in ("draft","wrong","ghost","corrected")):
        issues.append("blank opening damaged")
    if states[2]["wrong"]<=0 or states[3]["wrong"]<=states[2]["wrong"]:
        issues.append("mistake did not appear progressively")
    if states[4]["wrong"]>=states[3]["wrong"] or states[4]["ghost"]<=0:
        issues.append("erasure/ghost not preserved")
    if states[5]["corrected"]<=0:issues.append("no redraw")
    if states[7]!=states[8]:issues.append("pause changes pencil state")
    if any(states[-1][k] for k in ("draft","wrong","ghost","corrected")):
        issues.append("final original is not clean")
    return {"passed":not issues,"errors":issues,"video_generated":False,
            "provisional_lyric_timing":True,"redraw_occurrences":1}

if __name__=="__main__":
    result=quality_gate()
    print(json.dumps(result,ensure_ascii=False))
    if result["errors"]:raise SystemExit(1)
