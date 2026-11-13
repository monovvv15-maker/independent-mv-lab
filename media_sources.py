"""Free external footage metadata adapters. No media files are downloaded."""
import json
import re
from html import unescape
from urllib.parse import urlencode
from urllib.request import Request, urlopen

COMMONS_ENDPOINT = "https://commons.wikimedia.org/w/api.php"

def plain(value):
    return unescape(re.sub("<[^>]*>", "", str(value or "")))

def commons_license(meta):
    short = plain((meta.get("LicenseShortName") or {}).get("value", "")).lower().strip()
    allowed = short in {"cc0", "public domain", "pd", "cc by 4.0", "cc by 3.0", "cc by 2.0", "cc-by-4.0", "cc-by-3.0", "cc-by-2.0"}
    url = str((meta.get("LicenseUrl") or {}).get("value", ""))
    return short, url, allowed

def commons_search(query, limit=8, opener=urlopen):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:video", "gsrnamespace": 6,
        "gsrlimit": min(max(int(limit), 1), 50),
        "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": 480,
    }
    url = COMMONS_ENDPOINT + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "IndependentMVLab/0.4 (https://github.com/monovvv15-maker/independent-mv-lab)"})
    with opener(req, timeout=25) as response:
        data = json.load(response)
    rows = []
    for page in (data.get("query", {}).get("pages") or {}).values():
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        if not str(info.get("mime", "")).startswith("video/"):
            continue
        short, license_url, license_ok = commons_license(info.get("extmetadata") or {})
        download_url = info.get("url") or ""
        source_url = info.get("descriptionurl") or ""
        if not download_url.startswith("https://") or not source_url.startswith("https://"):
            continue
        rows.append({
            "id": "commons_" + str(page["pageid"]),
            "title": page.get("title", ""),
            "source": "commons",
            "source_url": source_url,
            "preview_url": info.get("thumburl") or "",
            "download_url": download_url,
            "license": short,
            "license_url": license_url,
            "author": plain((info.get("extmetadata") or {}).get("Artist", {}).get("value", ""))[:250],
            "license_ok": license_ok,
            "search_query": query,
        })
    return rows
