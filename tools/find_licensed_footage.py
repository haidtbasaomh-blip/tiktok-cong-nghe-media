#!/usr/bin/env python3
"""Research Wikimedia Commons MOVING FOOTAGE only, by exact file licensing.

No downloading at this stage; metadata, URL and license only.
No video is approved for publication by this search.
"""
from __future__ import annotations
import datetime as dt
import json, re, time, html, urllib.request, urllib.parse
from pathlib import Path

OUT=Path("series/verified_clip_candidates.json")
TERMS=[
"filetype:video waterfall nature",
"filetype:video flowing waterfall",
"filetype:video mountain landscape",
"filetype:video Vietnam nature",
"filetype:video rice terraces",
"filetype:video sunrise timelapse",
"filetype:video clouds mountains"
]
VALID={"CC0","CC BY 2.0","CC BY 3.0","CC BY 4.0","CC BY-SA 4.0","CC BY-SA 3.0","CC BY-SA 2.0","Public domain"}
BLOCK={"Non-free","Copyrighted free use","Fair use","Unknown"}
def text(x):
    return re.sub(r"\s+"," ",html.unescape(re.sub("<[^>]*>"," ",x or ""))).strip()
def fetch(term):
    data={
      "action":"query","generator":"search","gsrnamespace":"6","gsrsearch":term,"gsrlimit":"50",
      "prop":"imageinfo","iiprop":"url|mime|size|extmetadata","format":"json"
    }
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(data)
    req=urllib.request.Request(url,headers={"User-Agent":"GocCongNgheTienIch-Creative-Research/1.0 (educational license checker)"})
    with urllib.request.urlopen(req,timeout=35) as rsp:
        return (json.load(rsp).get("query") or {}).get("pages") or {}
def main():
    matches={}
    for term in TERMS:
        try:
            pages=fetch(term)
            print("SEARCH",term,"RESULTS",len(pages),flush=True)
        except Exception as exc:
            print("SEARCH_UNAVAILABLE",term,type(exc).__name__,flush=True)
            continue
        for page in pages.values():
            name=str(page.get("title") or "")
            if not re.search(r"\.(webm|ogv|mp4|mov)$",name,re.I):continue
            info=(page.get("imageinfo") or [{}])[0]
            if not ("video/" in str(info.get("mime") or "") or "ogg" in str(info.get("mime") or "")):continue
            ext=info.get("extmetadata") or {}
            license=text((ext.get("LicenseShortName") or {}).get("value"))
            if license not in VALID:continue
            source=str(info.get("url") or "")
            if not source.startswith("https://"):continue
            key=name.casefold()
            creator=text((ext.get("Artist") or {}).get("value"))[:110]
            credit=text((ext.get("Credit") or {}).get("value"))[:160]
            license_url=text((ext.get("LicenseUrl") or {}).get("value"))
            if license in {"CC BY 2.0","CC BY 3.0","CC BY 4.0","CC BY-SA 4.0","CC BY-SA 3.0","CC BY-SA 2.0"} and (not creator or not license_url):
                continue
            matches[key]={
              "name":name,"source_url":source,
              "page_url":"https://commons.wikimedia.org/wiki/"+name.replace(" ","_"),
              "license":license,"creator":creator or "unknown","credit":credit,
              "license_url":license_url,
              "bytes":int(info.get("size") or 0),
              "mime":info.get("mime"),
              "state":"LICENSE_METADATA_FOUND_NEEDS_VISUAL_AND_AUDIO_REVIEW",
              "note":"Source licensing must be revalidated upon use; no video automatically publishable."
            }
    collection=sorted(matches.values(),key=lambda r:(r["license"]=="CC0",r["bytes"]>1500000,-r["bytes"]),reverse=True)
    result={"checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "search_terms":TERMS,
        "candidates":collection[:100],
        "count":len(collection),
        "publication_authorized":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("VERIFIED_MOVING_FOOTAGE_LICENSE_METADATA_CANDIDATES",len(collection))
    for clip in collection[:25]:
        print("FOOTAGE",clip["name"],"LICENSE",clip["license"],"BYTES",clip["bytes"])
    if len(collection)<3:raise SystemExit("NOT_ENOUGH_LICENSED_MOVING_FOOTAGE_FOUND_FOR_TRIAL")
if __name__=="__main__":
    main()
