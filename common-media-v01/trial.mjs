// Shared media interface V01; no artwork, renderer, DB, UI or automatic generation.
// Source functions below are extracted verbatim from the two pinned successful pages.
// Fixed 150F scope. Other lengths require a separately approved adapter/qualification.
export const CONTRACT=Object.freeze({version:1,width:1920,height:1080,fps:30,total_frames:150,sample_rate:48000,channels:2,seconds:5,source_blobs:Object.freeze({v12:'49f88f80e0c46d21d1965096a10d90dc7359376c',v13_actor:'fa7118ac6bfbbec8d078fcead21b42c76d18cc98',v08:'43f5575644b76604e25392404271670346dd23b7'})});
const check=(p,m)=>{if(!p)throw Error(m)};
const isSha=x=>typeof x==='string'&&/^[0-9a-f]{64}$/.test(x);
const isId=x=>typeof x==='string'&&/^[a-z0-9][a-z0-9_-]{0,79}$/.test(x);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function validateJob(j){
 check(j&&j.schema_version===1&&isId(j.project_id)&&isId(j.adapter_id),'job identity');
 for(const k of ['recipe_sha256','manifest_sha256','adapter_sha256','source_audio_sha256','pcm_sha256'])check(isSha(j[k]),'missing pin '+k);
 for(const k of ['width','height','fps','total_frames','sample_rate','channels'])check(j[k]===CONTRACT[k],'unsupported '+k);
 check(Number.isSafeInteger(j.source_frames)&&Number.isSafeInteger(j.start_sample)&&j.start_sample>=0&&j.start_sample+240000<=j.source_frames,'audio sample range');
 check(j.generation_authorized===false&&j.max_cost===0,'job cannot grant approval');
 // Fixed field order, copied values, no unknown fields used by the execution core.
 const keys=['schema_version','project_id','adapter_id','adapter_sha256','recipe_sha256','manifest_sha256','source_audio_sha256','pcm_sha256','width','height','fps','total_frames','sample_rate','channels','source_frames','start_sample','generation_authorized','max_cost'];
 return Object.freeze(Object.fromEntries(keys.map(k=>[k,j[k]])));
}
export function validateApproval(approval,scope){
 check(approval&&approval.explicit_start_instruction==='動画生成開始'&&approval.private_only===true&&approval.max_cost===0,'explicit scoped approval required');
 const a=approval.scope;check(a&&Object.keys(a).length===Object.keys(scope).length&&Object.keys(scope).every(k=>a[k]===scope[k]),'approval scope mismatch');
 return true;
}
const SR=48000;
const hashBytes=async b=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",b)),n=>n.toString(16).padStart(2,"0")).join("");

function parseWav(bytes,expectedFrames=11982720){const d=new DataView(bytes),four=p=>String.fromCharCode(...new Uint8Array(bytes,p,4)),u=p=>d.getUint32(p,true);check(bytes.byteLength>=44&&four(0)==="RIFF"&&four(8)==="WAVE"&&u(4)+8===bytes.byteLength,"RIFF header");let fmt=null,data=null;
 for(let p=12;p<bytes.byteLength;){check(p+8<=bytes.byteLength,"truncated WAV chunk");const type=four(p),size=u(p+4),start=p+8,end=start+size;check(end+(size&1)<=bytes.byteLength,"WAV chunk bounds");if(type==="fmt "){check(!fmt&&size>=16,"WAV fmt");fmt={format:d.getUint16(start,true),channels:d.getUint16(start+2,true),rate:u(start+4),byteRate:u(start+8),align:d.getUint16(start+12,true),bits:d.getUint16(start+14,true)};}if(type==="data"){check(!data,"duplicate WAV data");data={start,size};}p=end+(size&1);}
 check(fmt&&data&&fmt.format===1&&fmt.channels===2&&fmt.rate===SR&&fmt.byteRate===SR*4&&fmt.align===4&&fmt.bits===16&&data.size===expectedFrames*4,"WAV PCM format/count");return {...fmt,frames:data.size/4,offset:data.start};
}
function slicePCM(bytes,meta,start,count){check(start>=0&&count>0&&start+count<=meta.frames,"PCM slice bounds");const d=new DataView(bytes,meta.offset+start*4,count*4),a=[new Float32Array(count),new Float32Array(count)];for(let k=0;k<count;k++)for(let c=0;c<2;c++)a[c][k]=d.getInt16(4*k+2*c,true)/32768;return a;}

export async function prepareTrial({job,recipeBytes,manifestBytes,sourceWav,assetFiles,adapter,notify=()=>{},externalGuard=()=>{}}){
 const scope=validateJob(job);
 check(adapter?.id===scope.adapter_id&&adapter?.revision===scope.adapter_sha256&&typeof adapter.renderFrames==='function','registered adapter identity mismatch');
 // Adapter implementation is trusted caller code; declaration alone is not cryptographic code attestation.
 const render=adapter.renderFrames.bind(adapter);
 const toBytes=async x=>x instanceof ArrayBuffer?x.slice(0):ArrayBuffer.isView(x)?x.buffer.slice(x.byteOffset,x.byteOffset+x.byteLength):await x.arrayBuffer();
 const [rb,mb,wb]=await Promise.all([toBytes(recipeBytes),toBytes(manifestBytes),toBytes(sourceWav)]);
 check(await hashBytes(rb)===scope.recipe_sha256&&await hashBytes(mb)===scope.manifest_sha256&&await hashBytes(wb)===scope.source_audio_sha256,'recipe/manifest/source SHA mismatch');
 const decode=b=>JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(b));
 const recipe=decode(rb),manifest=decode(mb);
 check(recipe.schema_version===1&&recipe.project_id===scope.project_id&&manifest.project_id===scope.project_id,'recipe identity');
 for(const k of ['width','height','fps','total_frames','source_audio_sha256'])check(recipe[k]===scope[k],'recipe scope mismatch '+k);
 check(Math.abs((recipe.start_song_seconds??0)*48000-scope.start_sample)<.0001,'recipe audio start');
 check(Array.isArray(manifest.assets)&&manifest.assets.length>0&&assetFiles instanceof Map,'manifest assets required');
 const assets=new Map();
 for(const a of manifest.assets){check(a&&typeof a.id==='string'&&!assets.has(a.id)&&isSha(a.sha256)&&assetFiles.has(a.id),'asset identity');const b=await toBytes(assetFiles.get(a.id));check(await hashBytes(b)===a.sha256,'asset SHA '+a.id);assets.set(a.id,b)}
 check(assetFiles.size===assets.size,'undeclared assets');
 const meta=parseWav(wb,scope.source_frames);
 check(await hashBytes(new Uint8Array(wb,meta.offset+scope.start_sample*4,960000))===scope.pcm_sha256,'PCM slice SHA');
 const pcm=slicePCM(wb,meta,scope.start_sample,240000);
 return makeSession({scope,recipe,manifest,assets,pcm,render,notify,externalGuard});
}
function makeSession({scope,recipe,manifest,assets,pcm,render,notify,externalGuard}){
 const W=1920,H=1080,FPS=30,N=150,D=5,SR=48000,SEG=150,PARTS=1,MAX_PART=12*1024*1024,MAX_FINAL=60*1024*1024,FRAME_BYTES=W*H*4,THUMB_W=128,THUMB_H=72;
 const RECIPE='COMMON-TRIAL-V01',IDENTITY=JSON.stringify(scope);
 let sourcePCM=pcm,permit=false,record=null,verified=null,busy=false,attempted=false,finished=false;
 const show=data=>notify(JSON.parse(JSON.stringify(data)));
 function generationGate(){check(permit&&record&&verified,'verified in-session mux only')}
 async function getPart(id){generationGate();check(id===0,'single segment scope');return record}
 async function run(approval,{muxOnly=false}={}){
  validateApproval(approval,scope);check(!busy&&!finished,'session busy or complete');
  check(muxOnly?!!(record&&verified):!attempted,'existing attempt protected; no automatic redraw');
  busy=true;permit=true;const start=performance.now();let output=null,finalized=false;
  const guard=()=>{check(permit&&performance.now()-start<300000,'session time limit');check(!document.hidden,'foreground required');externalGuard()};
  const data={version:'COMMON-TRIAL-V01',project_id:scope.project_id,scope,stage:'input',status:'RUNNING',submitted:muxOnly?150:0,media_generated:false,video_reencoded:false,checkpoint_written:false,playback:'UNVERIFIED',art:'REVIEW_REQUIRED'};
  try{
   guard();const m=await deadline(import('https://cdn.jsdelivr.net/npm/mediabunny@1.66.2/+esm'),30000,'Mediabunny');
   for(const k of ['Output','Mp4OutputFormat','BufferTarget','VideoSampleSource','VideoSample','AudioBufferSource','AudioSampleSink','Input','BlobSource','EncodedVideoPacketSource','EncodedPacketSink','CanvasSink'])check(typeof m[k]==='function','missing '+k);
   if(!muxOnly){
    attempted=true;data.stage='render';show(data);
    const target=new m.BufferTarget();output=new m.Output({format:new m.Mp4OutputFormat(),target});
    const vs=new m.VideoSampleSource({codec:'avc',fullCodecString:'avc1.640028',bitrate:8000000,keyFrameInterval:1,latencyMode:'quality'});
    output.addVideoTrack(vs,{frameRate:FPS});await deadline(output.start(),20000,'segment start');
    const raw=[],rawHashes=[];let consuming=false,open=true;
    async function consume(frame,pixels){
     check(open&&!consuming&&frame===raw.length&&frame<150&&ArrayBuffer.isView(pixels)&&pixels.BYTES_PER_ELEMENT===1&&pixels.byteLength===FRAME_BYTES,'RGBA frame contract / sequential await required');
     consuming=true;try{
      guard();const rgba=new Uint8Array(pixels.buffer,pixels.byteOffset,pixels.byteLength),small=reduceRGBA(rgba),stats=visualStats(small);
      check(stats.sd>2&&stats.mean>5&&stats.mean<250,'invalid frame '+frame);const hash=await hashBytes(rgba);
      const sample=new m.VideoSample(rgba,{format:'RGBA',codedWidth:W,codedHeight:H,timestamp:frame/FPS,duration:1/FPS});
      try{await deadline(vs.add(sample,frame===0?{keyFrame:true}:undefined),20000,'direct encode');raw.push(small);rawHashes.push(hash)}finally{sample.close()}
      data.submitted=raw.length;if(frame%5===0||frame===149)show(data);
     }finally{consuming=false}
    }
    // Rendering is exclusively supplied by the production team; never called by prepareTrial.
    try{await render({scope,recipe:JSON.parse(JSON.stringify(recipe)),manifest:JSON.parse(JSON.stringify(manifest)),assets:new Map([...assets].map(([k,b])=>[k,b.slice(0)])),guard,consume})}finally{open=false}
    guard();check(!consuming&&raw.length===150,'150 frames required');
    data.stage='segment_finalize';show(data);await deadline(output.finalize(),30000,'segment finalize');finalized=true;
    check(target.buffer&&target.buffer.byteLength>1024&&target.buffer.byteLength<=MAX_PART,'segment memory cap');
    const part=new Blob([target.buffer],{type:'video/mp4'}),r={id:0,recipe:RECIPE,identity:IDENTITY,start:0,count:150,blob:part,bytes:part.size,sha256:await sha256(part)};
    data.stage='segment_QA';show(data);const q=await verifyV12Segment(m,r,raw,rawHashes,guard);record=r;verified=q;
   }
   data.segment=verified.meta;data.stage='assemble';show(data);const b=await assemble(m,data,guard,[verified]);
   data.media_generated=true;data.stage='final_QA';show(data);data.file=await verifyV12Final(m,b,verified,guard);
   data.status='PASS_TECHNICAL_PLAYBACK_PENDING';data.stage='complete';data.playback='USER_CHECK_REQUIRED';data.elapsed_s=(performance.now()-start)/1000;finished=true;show(data);
   return {blob:b,report:data};
  }catch(e){data.status='FAIL';data.error=String(e);data.can_resume_mux=!!(record&&verified);show(data);return {report:data}}
  finally{if(output&&!finalized){try{await deadline(output.cancel(),3000,'cancel')}catch{}}permit=false;busy=false}
 }
 return Object.freeze({status:'PREPARED_NON_RENDER',scope,run,rendered:false,art:'REVIEW_REQUIRED'});
 // Extracted source functions, unchanged except no changes to their enclosing dependencies.
const delay=()=>new Promise(r=>setTimeout(r,0));
const deadline=(p,ms,label)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error(label+" timeout")),ms);Promise.resolve(p).then(v=>{clearTimeout(timer);resolve(v)},e=>{clearTimeout(timer);reject(e)})});

function audioBuffer(sec){check(sourcePCM&&Number.isInteger(sec)&&sec>=0&&sec<D,"real PCM not loaded");const b=new AudioBuffer({length:SR,numberOfChannels:2,sampleRate:SR});for(let ch=0;ch<2;ch++)b.copyToChannel(sourcePCM[ch].subarray(sec*SR,(sec+1)*SR),ch);return b;}

function audioMeter(){return {pcm:[new Float32Array(D*SR),new Float32Array(D*SR)],next:0,covered:0,coverage_errors:0,pre_samples:0,post_samples:0,peak:0,clips:0};}
function meterBlock(q,buf,ts){check(buf.sampleRate===SR&&buf.numberOfChannels===2,"audio format");const base=Math.round(ts*SR);check(Math.abs(ts*SR-base)<.1,"PCM grid");const a=[buf.getChannelData(0),buf.getChannelData(1)];for(let k=0;k<buf.length;k++){const i=base+k;if(i<0){q.pre_samples++;continue;}if(i>=D*SR){q.post_samples++;continue;}if(i!==q.next)q.coverage_errors++;q.next=i+1;q.covered++;for(let c=0;c<2;c++){const x=a[c][k];check(Number.isFinite(x),"nonfinite PCM");q.pcm[c][i]=x;q.peak=Math.max(q.peak,Math.abs(x));if(Math.abs(x)>=1)q.clips++;}}}
function corr(a,b,start,end,lag,stride=1){let sx=0,sy=0,xx=0,yy=0,xy=0,n=0;const lo=Math.max(start,-lag),hi=Math.min(end,b.length-lag);for(let i=lo;i<hi;i+=stride){const x=a[i],y=b[i+lag];sx+=x;sy+=y;xx+=x*x;yy+=y*y;xy+=x*y;n++;}const vx=xx-sx*sx/n,vy=yy-sy*sy/n;return n>1&&vx>1e-10&&vy>1e-10?(xy-sx*sy/n)/Math.sqrt(vx*vy):null;}
function rms(a,start,end){let ss=0;for(let i=start;i<end;i++)ss+=a[i]*a[i];return Math.sqrt(ss/(end-start));}
function alignWindow(a,b,start,end){const zero=corr(a,b,start,end,0);let coarse=[];for(let lag=-2400;lag<=2400;lag+=16){const c=corr(a,b,start,end,lag,16);if(c!==null)coarse.push([lag,c]);}coarse.sort((x,y)=>y[1]-x[1]||Math.abs(x[0])-Math.abs(y[0]));const candidates=new Set([0]);for(const [lag] of coarse.slice(0,4))for(let j=-16;j<=16;j++)if(Math.abs(lag+j)<=2400)candidates.add(lag+j);let ranked=[...candidates].map(lag=>[lag,corr(a,b,start,end,lag,4)??-1]).sort((x,y)=>y[1]-x[1]||Math.abs(x[0])-Math.abs(y[0]));const refined=[...new Set([0,...ranked.slice(0,5).map(x=>x[0])])].map(lag=>[lag,corr(a,b,start,end,lag)??-1]).sort((x,y)=>y[1]-x[1]||Math.abs(x[0])-Math.abs(y[0]));const [lag,correlation]=refined[0];return {lag_samples:lag,lag_ms:lag/SR*1000,correlation,zero_lag_correlation:zero,ambiguous:refined.slice(1).some(x=>Math.abs(x[0]-lag)>480&&x[1]>=correlation-.0001),pass:correlation>=.98&&Math.abs(lag)<=480};}
function assessAudio(q){check(sourcePCM,"missing source PCM");const rows=[];for(let c=0;c<2;c++)for(let sec=0;sec<D;sec++){const start=sec*SR,end=start+SR,ref=rms(sourcePCM[c],start,end),out=rms(q.pcm[c],start,end),db=20*Math.log10(Math.max(ref,1e-12)),gain=20*Math.log10(Math.max(out,1e-12)/Math.max(ref,1e-12));rows.push({channel:c,second:sec,input_rms_dbfs:db,output_rms_dbfs:20*Math.log10(Math.max(out,1e-12)),gain_db:gain,...(db>=-45?{valid:true,...alignWindow(sourcePCM[c],q.pcm[c],start,end)}:{valid:false,status:"LOW_SIGNAL_REVIEW"})});}
 const valid=rows.filter(x=>x.valid);return {coverage_pass:q.coverage_errors===0&&q.covered===D*SR&&q.next===D*SR,covered_sample_frames:q.covered,coverage_errors:q.coverage_errors,pre_samples:q.pre_samples,post_samples:q.post_samples,peak:q.peak,clips:q.clips,valid_windows:valid.length,windows_pass:valid.filter(x=>x.pass&&!x.ambiguous).length,pass:valid.length>0&&valid.every(x=>x.pass&&!x.ambiguous)&&q.clips===0,windows:rows,lag_search:"coarse-to-fine ±50ms, nonzero ambiguity fails"};}

function reduceRGBA(p){
 check(p.length===FRAME_BYTES,"wrong RGBA size");
 const a=new Uint8Array(THUMB_W*THUMB_H);
 for(let y=0;y<THUMB_H;y++)for(let x=0;x<THUMB_W;x++){
  let sum=0;for(let dy=0;dy<15;dy++)for(let dx=0;dx<15;dx++){
   const i=((y*15+dy)*W+x*15+dx)*4;
   sum+=.299*p[i]+.587*p[i+1]+.114*p[i+2];
  }a[y*THUMB_W+x]=Math.round(sum/225);
 }return a;
}


function transformThumb(a,mode){
 const out=new Uint8Array(a.length);
 for(let y=0;y<THUMB_H;y++)for(let x=0;x<THUMB_W;x++){
  const xx=mode==="flip_x"||mode==="flip_xy"?THUMB_W-1-x:x;
  const yy=mode==="flip_y"||mode==="flip_xy"?THUMB_H-1-y:y;
  out[y*THUMB_W+x]=a[yy*THUMB_W+xx];
 }return out;
}

function thumb(source){
 const q=document.createElement("canvas");q.width=THUMB_W;q.height=THUMB_H;
 const ctx=q.getContext("2d",{willReadFrequently:true});ctx.drawImage(source,0,0,THUMB_W,THUMB_H);
 const p=ctx.getImageData(0,0,THUMB_W,THUMB_H).data,a=new Uint8Array(THUMB_W*THUMB_H);
 for(let i=0;i<a.length;i++){const k=i*4;a[i]=Math.round(.299*p[k]+.587*p[k+1]+.114*p[k+2]);}
 q.width=1;q.height=1;return a;
}
function mad(a,b){check(a?.length===THUMB_W*THUMB_H&&b?.length===a.length,"missing visual thumbnail");let sum=0;for(let i=0;i<a.length;i++)sum+=Math.abs(a[i]-b[i]);return sum/a.length;}
function visualStats(a){let sum=0,sq=0;for(const x of a){sum+=x;sq+=x*x;}const mean=sum/a.length;return {mean,sd:Math.sqrt(Math.max(0,sq/a.length-mean*mean))};}
const round=x=>Number(x.toFixed(3));
function jumpGate(d,neighbors){return d<=Math.max(8,2.5*Math.max(...neighbors));}

function boundaryGate(d,left,right){return d>=.1&&jumpGate(d,[left,right]);}
function compactAssessment(q){return {status:q.status,input_motion:q.input_motion,output_motion:q.output_motion,ratio_failures:q.ratio_failures,alignment_failures:q.alignment_failures,max_same_timestamp_mad:Math.max(...q.frames.map(x=>x.same_timestamp_mad))};}

function audioEdit(bytes){
 const d=new DataView(bytes),four=p=>String.fromCharCode(...new Uint8Array(bytes,p,4)),u=p=>d.getUint32(p),i=p=>d.getInt32(p);
 const u64=p=>{const v=Number(d.getBigUint64(p));check(Number.isSafeInteger(v),"box integer overflow");return v;};
 const i64=p=>{const v=Number(d.getBigInt64(p));check(Number.isSafeInteger(v),"edit integer overflow");return v;};
 function boxes(start,end){const out=[];for(let p=start;p<end;){check(end-p>=8,"truncated MP4 box");let n=u(p),h=8;if(n===1){check(end-p>=16,"truncated extended box");n=u64(p+8);h=16;}else if(n===0)n=end-p;check(n>=h&&p+n<=end,"invalid MP4 box bounds");out.push({type:four(p+4),start:p+h,end:p+n});p+=n;}return out;}
 function children(b){return boxes(b.start,b.end);}
 function one(list,type){const x=list.filter(b=>b.type===type);check(x.length===1,"missing/ambiguous "+type);return x[0];}
 function scale(b){const v=d.getUint8(b.start);check(v===0||v===1,"unsupported header version");const p=b.start+(v===1?20:12);check(p+4<=b.end,"truncated timescale");const n=u(p);check(n>0,"invalid timescale");return n;}
 const moov=one(boxes(0,bytes.byteLength),"moov"),mc=children(moov),movie=scale(one(mc,"mvhd"));const tracks=mc.filter(b=>b.type==="trak").map(t=>{const c=children(t),md=children(one(c,"mdia")),h=one(md,"hdlr");check(h.start+12<=h.end,"truncated handler");return {c,md,type:four(h.start+8)};});
 const aud=tracks.filter(t=>t.type==="soun");check(aud.length===1,"audio track identity");
 const media=scale(one(aud[0].md,"mdhd")),ed=aud[0].c.filter(b=>b.type==="edts");
 if(!ed.length)return {present:false,movie_timescale:movie,media_timescale:media,entries:[]};
 check(ed.length===1,"multiple edit boxes");const e=one(children(ed[0]),"elst"),v=d.getUint8(e.start);check(v===0||v===1,"unsupported edit version");check(e.start+8<=e.end,"truncated elst");
 const n=u(e.start+4),stride=v===1?20:12;check(n<=8&&e.start+8+n*stride===e.end,"edit entry size");const entries=[];
 for(let j=0;j<n;j++){const p=e.start+8+j*stride,seg=v===1?u64(p):u(p),mt=v===1?i64(p+8):i(p+4),rate=i(p+(v===1?16:8))/65536;entries.push({duration_s:seg/movie,media_time_s:mt===-1?null:mt/media,media_rate:rate});}
 return {present:true,movie_timescale:movie,media_timescale:media,entries};
}
function presentationCheck(edit,pFirst,pEnd,dFirst,dEnd){
 const near=(x,y,t)=>Number.isFinite(x)&&Math.abs(x-y)<=t;
 const raw=Number.isFinite(pFirst)&&Number.isFinite(dFirst)&&pFirst<=.05&&dFirst<=.05&&near(pEnd,D,.1)&&near(dEnd,D,.1);
 if(!raw)return false;
 if(pFirst<-.0001||dFirst<-.0001){
  if(!edit.present||edit.entries.length!==1)return false;
  const e=edit.entries[0];
  return e.media_rate===1&&e.media_time_s>0&&near(-pFirst,e.media_time_s,.002)&&near(-dFirst,e.media_time_s,.002)&&near(e.duration_s,D,.1)&&dEnd>=D-1/SR;
 }
 return !edit.present&&near(pFirst,0,.05)&&near(dFirst,0,.05);
}
const sha256=async b=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",await b.arrayBuffer())),n=>n.toString(16).padStart(2,"0")).join("");

function frameIndex(t,start){const x=(t-start)*FPS,n=Math.round(x);check(Math.abs(x-n)<0.015&&n>=0&&n<SEG,"off-grid segment timestamp: "+t);return n;}
function validRecord(r,id){return r?.id===id&&r.recipe===RECIPE&&r.identity===IDENTITY&&r.start===id*SEG&&r.count===SEG&&r.blob instanceof Blob&&r.blob.size===r.bytes&&r.bytes>1024&&r.bytes<=MAX_PART&&/^[0-9a-f]{64}$/.test(r.sha256);}
async function configSignature(c){
 check(c&&c.description&&c.codec&&c.codedWidth===W&&c.codedHeight===H,"missing AVC decoder config");
 const desc=c.description instanceof ArrayBuffer?new Uint8Array(c.description):new Uint8Array(c.description.buffer,c.description.byteOffset,c.description.byteLength);
 return JSON.stringify([c.codec,c.codedWidth,c.codedHeight,c.displayAspectWidth??null,c.displayAspectHeight??null,c.colorSpace?.primaries??null,c.colorSpace?.transfer??null,c.colorSpace?.matrix??null,c.colorSpace?.fullRange??null,await sha256(new Blob([desc]))]);
}


async function muxPart(m,r,id,expected,guard,consume){
 check(validRecord(r,id)&&r.sha256===expected.meta.sha256&&await sha256(r.blob)===r.sha256,"mux source changed");
 const input=new m.Input({source:new m.BlobSource(r.blob),formats:m.ALL_FORMATS});
 try{
  const v=await input.getPrimaryVideoTrack(),cfg=await v.getDecoderConfig(),sig=await configSignature(cfg),first=await v.getFirstTimestamp();
  check(sig===expected.meta.config_signature,"mux config changed");let count=0;const seen=new Set();
  for await(const p of new m.EncodedPacketSink(v).packets(undefined,undefined,{verifyKeyPackets:true})){
   guard();const n=frameIndex(p.timestamp,first);check(!seen.has(n)&&await hashBytes(p.data)===expected.hashes[n],"mux packet changed");seen.add(n);
   await consume(p,n,cfg,sig,count++);
  }check(count===SEG,"mux segment count");
 }finally{input.dispose();}
}

async function assemble(m,data,guard,verified){
 generationGate();
 let output=null,finalized=false;
 try{
  const target=new m.BufferTarget();output=new m.Output({format:new m.Mp4OutputFormat(),target});
  const vs=new m.EncodedVideoPacketSource("avc"),as=new m.AudioBufferSource({codec:"aac",bitrate:192000});
  output.addVideoTrack(vs,{frameRate:FPS});output.addAudioTrack(as);await deadline(output.start(),20000,"assembly start");
  let signature=null,sequence=0,audioSec=0;
  for(let id=0;id<PARTS;id++){
   guard();const rec=await getPart(id);
   await muxPart(m,rec,id,verified[id],guard,async(pkt,n,cfg,sig,count)=>{
    if(signature===null)signature=sig;
    check(sig===signature,"AVC configuration differs across segments; safe stop, no remux");
    await deadline(vs.add(pkt.clone({timestamp:(id*SEG+n)/FPS,duration:1/FPS,sequenceNumber:sequence++}),count===0?{decoderConfig:cfg}:undefined),20000,"packet mux");
    // Interleave audio in approximately one-second steps to bound mux buffering.
    while(audioSec<D&&audioSec<=Math.floor((id*SEG+count)/FPS)){guard();await deadline(as.add(audioBuffer(audioSec++)),20000,"audio mux");}
   });
   data.muxed_video_packets=sequence;data.muxed_audio_seconds=audioSec;show(data);await delay();
  }
  while(audioSec<D){guard();await deadline(as.add(audioBuffer(audioSec++)),20000,"audio mux");}
  check(sequence===N&&audioSec===D,"assembly count mismatch");guard();
  await deadline(output.finalize(),45000,"assembly finalize");finalized=true;
  check(target.buffer&&target.buffer.byteLength<=MAX_FINAL&&target.buffer.byteLength>1024,"final memory cap or empty MP4");
  data.muxed_video_packets=sequence;data.muxed_audio_seconds=audioSec;
  return new Blob([target.buffer],{type:"video/mp4"});
 }finally{if(output&&!finalized){try{await deadline(output.cancel(),3000,"cancel assembly");}catch{}}}
}

async function verifyV12Segment(m,r,raw,rawHashes,guard){
 check(validRecord(r,0)&&await sha256(r.blob)===r.sha256,'V12 segment SHA');
 const input=new m.Input({source:new m.BlobSource(r.blob),formats:m.ALL_FORMATS});
 try{
  const v=await input.getPrimaryVideoTrack();check(v&&!(await input.getPrimaryAudioTrack()),'segment tracks');
  check(await v.getCodec()==='avc'&&await v.getDisplayWidth()===W&&await v.getDisplayHeight()===H,'segment format');
  const config=await configSignature(await v.getDecoderConfig()),first=await v.getFirstTimestamp();check(Math.abs(first)<.002,'segment first PTS');
  const hashes=[],seen=new Set();let n=0;
  for await(const p of new m.EncodedPacketSink(v).packets(undefined,undefined,{verifyKeyPackets:true})){
   guard();const i=frameIndex(p.timestamp,first);check(!seen.has(i)&&Math.abs(p.duration-1/FPS)<.002,'packet grid');
   if(!n)check(i===0&&p.type==='key','first keyframe');seen.add(i);hashes[i]=await hashBytes(p.data);n++;
  }
  check(n===150&&seen.size===150,'packet count');
  const frames=[],diffs=[],adj=[],orientation=[];
  for await(const f of new m.CanvasSink(v,{width:THUMB_W,height:THUMB_H,fit:'contain'}).canvases()){
   guard();const i=frames.length;check(i<150&&Math.abs(f.timestamp-first-i/FPS)<.002,'segment decoded PTS');
   const x=thumb(f.canvas),st=visualStats(x);check(st.sd>2&&st.mean>5&&st.mean<250,'segment invalid pixels');
   const d=mad(raw[i],x);diffs.push(d);check(d<=8,'raw/decoded frame mismatch F'+i);
   for(const mode of ['flip_x','flip_y','flip_xy'])check(mad(raw[i],transformThumb(x,mode))>=d-.1,'orientation mismatch F'+i);
   if(i)adj.push(mad(frames[i-1],x));frames.push(x);
  }
  check(frames.length===150,'segment decode count');check(new Set(rawHashes).size>1&&adj.some(x=>x>0),'all frames static');
  return {frames,hashes,meta:{id:0,frames:150,bytes:r.bytes,sha256:r.sha256,config_signature:config,visual:{raw_unique_sha:new Set(rawHashes).size,max_same_timestamp_mad:Math.max(...diffs),decoded_adjacent_mad_min:Math.min(...adj),decoded_adjacent_mad_max:Math.max(...adj),low_motion_frames:adj.flatMap((x,i)=>x<.1?[i+1]:[]),motion_qualification:'localized conductor motion; perceptual motion/art review required'}}};
 }finally{input.dispose()}
}
async function verifyV12Final(m,b,q,guard){
 const input=new m.Input({source:new m.BlobSource(b),formats:m.ALL_FORMATS});
 try{
  const v=await input.getPrimaryVideoTrack(),a=await input.getPrimaryAudioTrack();check(v&&a,'final tracks');
  const [width,height,vc,ac,vd,ad,du,first]=await Promise.all([v.getDisplayWidth(),v.getDisplayHeight(),v.getCodec(),a.getCodec(),v.computeDuration(),a.computeDuration(),input.computeDuration(),v.getFirstTimestamp()]);
  check(width===W&&height===H&&vc==='avc'&&ac==='aac'&&Math.abs(first)<.002&&Math.abs(vd-5)<.05&&Math.abs(ad-5)<.10&&Math.abs(du-5)<.10,'final format or duration');
  check(await configSignature(await v.getDecoderConfig())===q.meta.config_signature,'final config');
  const seen=new Set();let n=0;
  for await(const p of new m.EncodedPacketSink(v).packets(undefined,undefined,{verifyKeyPackets:true})){
   guard();const i=frameIndex(p.timestamp,first);check(!seen.has(i)&&Math.abs(p.duration-1/FPS)<.002&&await hashBytes(p.data)===q.hashes[i],'final packet mismatch');
   if(!n)check(i===0&&p.type==='key','final first key');seen.add(i);n++;
  }
  check(n===150,'final packet count');let fnum=0,maxMad=0;
  for await(const f of new m.CanvasSink(v,{width:THUMB_W,height:THUMB_H,fit:'contain'}).canvases()){
   guard();check(fnum<150&&Math.abs(f.timestamp-first-fnum/FPS)<.002,'final decoded PTS');
   const d=mad(thumb(f.canvas),q.frames[fnum]);check(d<=1,'final decoded frame differs');maxMad=Math.max(maxMad,d);fnum++;
  }
  check(fnum===150,'final decoded count');
  let apFirst=null,apEnd=null,packets=0,gap=0;
  for await(const p of new m.EncodedPacketSink(a).packets()){
   guard();if(apFirst===null)apFirst=p.timestamp;if(apEnd!==null)gap=Math.max(gap,Math.abs(p.timestamp-apEnd));apEnd=p.timestamp+p.duration;packets++;
  }
  let aFirst=null,aEnd=null,blocks=0,dgap=0,rate=null,channels=null;
  const meter=audioMeter(),edit=audioEdit(await b.arrayBuffer());
  for await(const z of new m.AudioSampleSink(a).samples()){
   try{guard();if(aFirst===null)aFirst=z.timestamp;if(aEnd!==null)dgap=Math.max(dgap,Math.abs(z.timestamp-aEnd));aEnd=z.timestamp+z.duration;const buf=z.toAudioBuffer();rate=buf.sampleRate;channels=buf.numberOfChannels;meterBlock(meter,buf,z.timestamp);blocks++}finally{z.close()}
  }
  const wave=assessAudio(meter),checks={format:packets>0&&blocks>0&&rate===48000&&channels===2,continuity:gap<=.002&&dgap<=.002,edit_presentation:presentationCheck(edit,apFirst,apEnd,aFirst,aEnd),pcm_coverage:wave.coverage_pass,real_pcm_alignment:wave.pass};
  check(Object.values(checks).every(Boolean),'audio QA '+JSON.stringify({checks,wave}));
  return {width,height,video_codec:'h264',audio_codec:'aac-lc',video_duration:vd,audio_duration:ad,duration:du,packets:n,decoded_frames:fnum,packet_hashes_verified:n,max_segment_to_final_mad:maxMad,bytes:b.size,sha256:await sha256(b),audio:{checks,packets,decoded_blocks:blocks,rate,channels,edit,wave,max_packet_gap_s:gap,max_decoded_gap_s:dgap}};
 }finally{input.dispose()}
}

}
