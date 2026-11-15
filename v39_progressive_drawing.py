"""V39 deterministic procedural drawing renderer: PREPARATION ONLY.
Input source jacket must be provided privately at render time. Do not upload it
to public GitHub. No output is produced by importing this module.
The authorized future renderer will expose frames to ffmpeg.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import cv2

EXPECTED_SOURCE_SHA256="084ee0c5b601b4e2bd612e9314db8237d722998f8b6727cdfe7eb7bd7da91dba"
DURATION=199.872
SIZE=720
FPS=24
# Title occupies upper-right area of the actual 1536x1536 jacket.
# These are loose ROI proportions; dark-stroke threshold isolates letters.
TITLE_ROI=(.685,.040,.980,.125)
PHASES=[
 ("blank",0.,12.),
 ("road_lines",12.,40.),
 ("railway_poles",40.,70.),
 ("houses_memory",70.,111.),
 ("pause",111.,139.),
 ("little_details",139.,161.),
 ("color_growth",161.,190.),
 ("full_jacket",190.,194.),
 ("title",194.,DURATION)
]
# Reveal from road vanishing point, foreground then scene edges.
# Continuous terrain progress is non-uniform to prevent flat global fading.
REGIONS={
 "road":(0.13,0.58,0.90,1.0),
 "rail_crossing":(0.11,0.23,0.89,0.80),
 "houses":(0.0,0.27,1.0,0.82),
 "sky":(0.0,0.0,1.0,0.43)
}
def input_hash(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def validated_image(path,strict=True):
    p=Path(path)
    if strict and input_hash(p)!=EXPECTED_SOURCE_SHA256:
        raise ValueError("Jacket original SHA mismatch")
    src=cv2.imread(str(p),cv2.IMREAD_COLOR)
    if src is None or src.shape[:2]!=(1536,1536):
        raise ValueError("Expected exact 1536 x 1536 jacket source")
    return cv2.resize(src,(SIZE,SIZE),interpolation=cv2.INTER_AREA)

def title_mask(im):
    h,w=im.shape[:2]
    x0,y0,x1,y1=(int(TITLE_ROI[0]*w),int(TITLE_ROI[1]*h),
                 int(TITLE_ROI[2]*w),int(TITLE_ROI[3]*h))
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    result=np.zeros((h,w),np.uint8)
    roi=gray[y0:y1,x0:x1]
    # letters are dark against sky. Exclude bright clouds with conservative mask.
    dark=cv2.inRange(roi,0,113)
    dark=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    result[y0:y1,x0:x1]=dark
    return result

def base_without_title(im):
    mask=title_mask(im)
    # Inpaint around dark lettering, not the whole sky rectangle.
    dilated=cv2.dilate(mask,np.ones((5,5),np.uint8))
    return cv2.inpaint(im,dilated,4,cv2.INPAINT_TELEA)

def progress(t,start,end):
    if end<=start:raise ValueError("invalid phase")
    return np.clip((t-start)/(end-start),0,1)

def stage_at(t):
    if t<0 or t>DURATION:raise ValueError("time outside song")
    for name,a,b in PHASES:
        if t<b or name=="title":return name
    return "title"

def make_draw_map(shape):
    h,w=shape[:2]
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    xx/=max(1,w-1);yy/=max(1,h-1)
    # A spatially varying reveal order: road near center -> tracks -> houses -> sky.
    # Deterministic wave prevents giant rectangular wipe.
    order=(.63*yy + .19*np.abs(xx-.5)
           +.08*np.sin(xx*17+yy*11)
           +.04*np.sin(xx*35-yy*25))
    order=(order-order.min())/(order.max()-order.min())
    return np.clip(order,0,1)

def derive_pencil(im):
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    smooth=cv2.bilateralFilter(gray,7,42,42)
    edge=cv2.Canny(smooth,33,90)
    # Blend sparse structural lines with shadow detail.
    shadows=cv2.adaptiveThreshold(smooth,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV,17,8)
    strokes=cv2.max(edge,(shadows*.43).astype(np.uint8))
    strokes[title_mask(im)>0]=0
    return strokes

def frame_at(t,im,clean=None,pencil=None,order=None):
    """Return one BGR frame. No text or new geometry is invented."""
    if clean is None:clean=base_without_title(im)
    if pencil is None:pencil=derive_pencil(im)
    if order is None:order=make_draw_map(im.shape)
    stage=stage_at(t)
    paper=np.full_like(im,(231,238,241),dtype=np.uint8) # off-white BGR
    # Traces of the picture accumulate and do not reset in the pause interval.
    if t<111:
        p=progress(t,12,111)*.89
    elif t<139:
        p=.89 # deliberate complete hold during the core message
    else:
        p=.89+.11*float(progress(t,139,161))
    revealed=(order<=p).astype(np.float32)[...,None]
    line_alpha=(pencil.astype(np.float32)/255.*.83*revealed)
    frame=(paper.astype(np.float32)*(1-line_alpha)+
           np.array((107,102,103),np.float32)*line_alpha)
    if t>=161:
        # Color lives inside already drawn details, grows with spatial order,
        # rather than a simultaneous crossfade of a fully visible photo.
        color_p=float(progress(t,161,190))
        colorful=(order<=color_p).astype(np.float32)[...,None]
        # Softer late-stage color improves original nostalgic look.
        color_strength=(.15+.85*color_p)*colorful
        frame=frame*(1-color_strength)+clean.astype(np.float32)*color_strength
    if t>=190:
        full=float(progress(t,190,194))
        frame=frame*(1-full)+clean.astype(np.float32)*full
    if t>=194:
        # Preserve the source's original handwritten strokes as final sign-off.
        mask=(title_mask(im).astype(np.float32)/255.)
        reveal=float(progress(t,194,DURATION))
        h,w=mask.shape
        xx=np.arange(w,dtype=np.float32)[None,:]
        x0=TITLE_ROI[0]*w;x1=TITLE_ROI[2]*w
        sweep=np.clip((reveal-(xx-x0)/(x1-x0))/.12,0,1)
        opacity=(mask*sweep)[...,None]
        frame=frame*(1-opacity)+im.astype(np.float32)*opacity
    return np.clip(frame,0,255).astype(np.uint8)

def validate_story():
    errors=[]
    if PHASES[0][0]!="blank" or PHASES[-1][0]!="title":errors.append("opening/ending")
    for i,(name,start,end) in enumerate(PHASES):
        if end<=start:errors.append("bad interval "+name)
        if i and abs(start-PHASES[i-1][2])>.0001:errors.append("gap "+name)
    if PHASES[-1][2]!=DURATION:errors.append("wrong duration")
    if stage_at(120)!="pause":errors.append("pause missing")
    return errors

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-only",action="store_true")
    ap.add_argument("--private-image")
    args=ap.parse_args()
    problems=validate_story()
    if args.private_image:
        validated_image(args.private_image)
    print(json.dumps({"stage_count":len(PHASES),"duration":DURATION,
      "source_sha":EXPECTED_SOURCE_SHA256,"video_created":False,
      "errors":problems},ensure_ascii=False))
    if problems:raise SystemExit(1)
