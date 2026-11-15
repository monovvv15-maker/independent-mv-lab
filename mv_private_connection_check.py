"""Read-only Dropbox connection preflight for private MV pipeline.

Do not download artwork/audio, create public artifacts or emit secrets.
Checks environment presence and Dropbox paths using metadata endpoint only.
"""
import json
import os
import urllib.request
from urllib.error import HTTPError
from mv_private_dropbox import access_token,safe_dropbox_path

NAMES=("DROPBOX_REFRESH_TOKEN","DROPBOX_APP_KEY","DROPBOX_APP_SECRET",
       "MV_JACKET_DROPBOX_PATH","MV_AUDIO_DROPBOX_PATH","MV_PRIVATE_CACHE_PATH")

def check_environment(environ=None):
    env=os.environ if environ is None else environ
    return {name:bool(env.get(name)) for name in NAMES}

def metadata(token,path):
    req=urllib.request.Request("https://api.dropboxapi.com/2/files/get_metadata",
       method="POST",data=json.dumps({"path":safe_dropbox_path(path)}).encode())
    req.add_header("Authorization","Bearer "+token)
    req.add_header("Content-Type","application/json")
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.load(response)

def check_sources():
    flags=check_environment()
    report={"config_flags":flags,"private_jacket_verified":False,
      "private_audio_verified":False,"cache_parent_verified":False,
      "ready":False,"no_video_generated":True,"no_private_bytes_downloaded":True}
    if not all(flags.values()):
        report["reason"]="required configuration incomplete"
        return report
    try:
        token=access_token()
    except HTTPError as error:
        report["auth_http_status"]=error.code
        report["reason"]="Dropbox OAuth refresh failed"
        return report
    for env,name in [("MV_JACKET_DROPBOX_PATH","private_jacket_verified"),
                     ("MV_AUDIO_DROPBOX_PATH","private_audio_verified")]:
        try:
            info=metadata(token,os.environ[env])
            report[name]=(info.get(".tag")=="file")
        except Exception:
            report[name]=False
    cache_path=safe_dropbox_path(os.environ["MV_PRIVATE_CACHE_PATH"])
    parent=cache_path.rsplit("/",1)[0]
    try:
        info=metadata(token,parent)
        report["cache_parent_verified"]=(info.get(".tag")=="folder")
    except Exception:
        report["cache_parent_verified"]=False
    report["ready"]=bool(report["private_jacket_verified"] and
       report["private_audio_verified"] and report["cache_parent_verified"])
    if not report["ready"]:report["reason"]="one or more Dropbox paths unavailable"
    return report

if __name__=="__main__":
    try:
        result=check_sources()
    except Exception as e:
        result={"ready":False,"no_video_generated":True,
             "error_type":type(e).__name__,
             "http_status":e.code if isinstance(e,HTTPError) else None,
             "reason":"Dropbox token or API unavailable"}
    print(json.dumps(result,ensure_ascii=False))
    if not result["ready"]:raise SystemExit(1)
