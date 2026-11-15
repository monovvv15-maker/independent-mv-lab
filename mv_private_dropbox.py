"""Dropbox private-media bridge for PUBLIC GitHub repository.

Never print access/refresh tokens or private file content. The public workflow
must not publish original media or audio-bearing MP4 as GitHub Artifacts.
Paths are configured in GitHub environment variables; secrets remain secrets.
"""
import argparse
import base64
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

TOKEN_URL="https://api.dropboxapi.com/oauth2/token"
CONTENT_URL="https://content.dropboxapi.com/2/files/"
def access_token():
    secret=os.environ.get("DROPBOX_REFRESH_TOKEN")
    key=os.environ.get("DROPBOX_APP_KEY")
    client_secret=os.environ.get("DROPBOX_APP_SECRET")
    if not (secret and key and client_secret):
        raise RuntimeError("Missing one-time Dropbox credentials (fail closed)")
    body=urllib.parse.urlencode({"grant_type":"refresh_token",
       "refresh_token":secret,"client_id":key,"client_secret":client_secret}).encode()
    req=urllib.request.Request(TOKEN_URL,data=body,method="POST")
    req.add_header("Content-Type","application/x-www-form-urlencoded")
    with urllib.request.urlopen(req,timeout=45) as resp:
        token=json.load(resp).get("access_token")
    if not token:raise RuntimeError("Dropbox refresh response contained no access token")
    return token

def safe_dropbox_path(path):
    if not path or not path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("Dropbox path must be absolute and without traversal")
    if len(path)>600:raise ValueError("Path too long")
    return path

def api_request(token,endpoint,path,data=None):
    req=urllib.request.Request(CONTENT_URL+endpoint,
        data=(data if data is not None else b""),
        method="POST")
    req.add_header("Authorization","Bearer "+token)
    req.add_header("Dropbox-API-Arg",json.dumps({"path":safe_dropbox_path(path)},
      separators=(",",":")))
    if data is not None:
        req.add_header("Content-Type","application/octet-stream")
    return urllib.request.urlopen(req,timeout=240)

def download(token,remote,local,optional=False):
    target=Path(local)
    try:
        with api_request(token,"download",remote) as resp:
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open("wb") as fp:
                while True:
                    chunk=resp.read(1024*1024)
                    if not chunk:break
                    fp.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        if optional:return False
        raise
    return True

def upload(token,local,remote):
    src=Path(local)
    if not src.is_file():raise FileNotFoundError(src)
    data=src.read_bytes()
    if len(data)>140*1024*1024:
        raise ValueError("File > 140MiB requires Dropbox upload sessions")
    req=urllib.request.Request(CONTENT_URL+"upload",data=data,method="POST")
    req.add_header("Authorization","Bearer "+token)
    req.add_header("Dropbox-API-Arg",json.dumps(
        {"path":safe_dropbox_path(remote),"mode":"overwrite","autorename":False},
        separators=(",",":")))
    req.add_header("Content-Type","application/octet-stream")
    with urllib.request.urlopen(req,timeout=240) as response:
        result=json.load(response)
    if not result.get("id"):raise RuntimeError("Dropbox did not return file id")
    return result["id"]

def backup_workspace(work,archive):
    """Receipts, derivative products and logs only. Never raw original media."""
    root=Path(work)
    safe=["receipts","products","logs","qa.json","preflight.json","delivery.json","last_run.json"]
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for name in safe:
            path=root/name
            if path.is_file():
                z.write(path,name)
            elif path.is_dir():
                for f in path.rglob("*"):
                    if f.is_file():z.write(f,str(f.relative_to(root)))
    return archive

def restore_workspace(archive,work):
    root=Path(work);root.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for f in z.infolist():
            dest=(root/f.filename).resolve()
            if not dest.is_relative_to(root.resolve()):
                raise ValueError("Unsafe cache archive traversal")
            if not f.is_dir():
                dest.parent.mkdir(parents=True,exist_ok=True)
                with z.open(f) as source,dest.open("wb") as target:
                    import shutil
                    shutil.copyfileobj(source,target)
    return root

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["fetch","restore","publish"])
    p.add_argument("--root",default=".mv-build")
    a=p.parse_args()
    token=access_token()
    root=Path(a.root)
    cache=os.environ.get("MV_PRIVATE_CACHE_PATH")
    if a.action=="fetch":
        image=os.environ.get("MV_JACKET_DROPBOX_PATH")
        audio=os.environ.get("MV_AUDIO_DROPBOX_PATH")
        if not image or not audio:raise RuntimeError("Required private source paths missing")
        download(token,image,".private-assets/jacket.jpg")
        download(token,audio,".private-assets/audio.mp3")
        print("Private source files acquired (no content or tokens logged)")
    elif a.action=="restore":
        if not cache:raise RuntimeError("Missing private cache path")
        zipfile_path=Path(".private-assets/cache.zip")
        if download(token,cache,zipfile_path,optional=True):
            restore_workspace(zipfile_path,root)
            print("Private resume archive restored")
        else:print("No prior private cache: new build")
    else:
        if not cache:raise RuntimeError("Missing private cache path")
        archive=Path(".private-assets/cache-new.zip")
        archive.parent.mkdir(exist_ok=True)
        backup_workspace(root,archive)
        upload(token,archive,cache)
        print("Private build and stage receipts persisted to Dropbox")
        # Original media is never written to Dropbox a second time.
if __name__=="__main__":main()
