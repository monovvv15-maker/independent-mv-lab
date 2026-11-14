"""V23 no-generation storyboard preflight."""
import json
SHOTS=[
('intro_neighborhood',40456181,'https://www.pexels.com/video/quiet-suburban-neighborhood-in-spring-40456181/',6.0),
('rain_puddle',13749224,'https://www.pexels.com/video/rainfall-over-puddle-13749224/',5.0),
('shoes_indoor',4953053,'https://www.pexels.com/video/low-angle-view-of-a-person-putting-on-the-shoe-and-tying-it-4953053/',5.0),
('walking_white',4464905,'https://www.pexels.com/video/person-walking-on-concrete-floor-4464905/',5.0),
('window',5835695,'https://www.pexels.com/video/a-person-opening-a-window-5835695/',5.0),
('neighborhood_outro',34381897,'https://www.pexels.com/video/quiet-urban-street-scene-with-lush-trees-34381897/',4.0)]
DURATIONS={40456181:21,13749224:32,4953053:9,4464905:10,5835695:9,34381897:9}
SONG_SHA256='d6615b1116569d603e2e630db9b08da0b065cd8208f877bb04c1d3ad63057764'
def validate(shots=SHOTS):
 errors=[];total=0;ids=set()
 for name,ident,url,sec in shots:
  if ident in ids:errors.append('duplicate '+str(ident))
  ids.add(ident)
  if not url.startswith('https://www.pexels.com/video/') or not url.endswith(f'-{ident}/'):errors.append('url mismatch '+name)
  if sec<=0 or sec>DURATIONS.get(ident,0):errors.append('short source '+name)
  total+=sec
 if abs(total-30)>0.001:errors.append('not 30 seconds')
 return errors
if __name__=='__main__':
 print(json.dumps({'source_clips':len(SHOTS),'duration_sec':sum(x[3] for x in SHOTS),'timing':'provisional, not lyric-verified','video_generated':False,'errors':validate()},ensure_ascii=False))
 if validate():raise SystemExit(1)
