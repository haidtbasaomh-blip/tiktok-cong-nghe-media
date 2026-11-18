#!/usr/bin/env python3
"""Find NASA Image Library official videos as an alternate source (metadata only)."""
import datetime,json,urllib.request,urllib.parse
from pathlib import Path

UA={"User-Agent":"GocCongNgheTienIch NASA source researcher 1.0"}
QUERIES=["aurora international space station","earth from international space station","earth timelapse space"]
OUT=Path("series/nasa_video_candidates.json")

def request(url):
    r=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(r,timeout=22) as res:
        if not (res.geturl().startswith("https://images-api.nasa.gov/") or res.geturl().startswith("https://images-assets.nasa.gov/")):
            raise RuntimeError("UNTRUSTED_NASA_REDIRECT")
        return json.load(res)

def main():
    results=[]
    for q in QUERIES:
        url="https://images-api.nasa.gov/search?"+urllib.parse.urlencode({"q":q,"media_type":"video","page_size":12})
        try:
            data=request(url)
            entries=((data.get("collection") or {}).get("items") or [])
            print("NASA_IMAGE_API_SEARCH",q,"RESULTS",len(entries),flush=True)
        except Exception as e:
            print("NASA_API_NOT_AVAILABLE",q,type(e).__name__,str(e)[:150],flush=True)
            continue
        for item in entries[:5]:
            info=(item.get("data") or [{}])[0]
            id=str(info.get("nasa_id") or "")
            href=str(item.get("href") or "")
            if not id or not (href.startswith("https://images-api.nasa.gov/") or href.startswith("https://images-assets.nasa.gov/")):
                print("NASA_ASSET_INDEX_URL_NOT_ALLOWED",id,href[:140],flush=True)
                continue
            try:
                assets=request(href)
            except Exception as e:
                print("ASSET_INDEX_ERROR",id,type(e).__name__,flush=True)
                continue
            if isinstance(assets,list):
                options=assets
            elif isinstance(assets,dict):
                options=(assets.get("collection") or {}).get("items") or []
            else:
                options=[]
            urls=[x.get("href") for x in options if isinstance(x,dict) and str(x.get("href") or "").lower().endswith((".mp4",".webm"))]
            if not urls:continue
            small=sorted(urls,key=lambda x:("~mobile" not in x and "~small" not in x and "~preview" not in x, len(x)))
            result={"nasa_id":id,"title":str(info.get("title") or "")[:160],"description":str(info.get("description") or "")[:800],
                    "source_url":"https://images.nasa.gov/details/"+urllib.parse.quote(id),
                    "best_video_candidate":small[0],
                    "other_video_urls":urls[:10],"status":"METADATA_ONLY_NOT_LICENSED_OR_APPROVED"}
            results.append(result)
            print("NASA_VIDEO_ASSET_CANDIDATE",id,"MEDIA",small[0][:150],flush=True)
    OUT.write_text(json.dumps({"checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "sources":results,"publish_permitted":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("NASA_ALTERNATE_VIDEO_ASSETS_FOUND",len(results),flush=True)
    if not results:raise SystemExit("NASA_NO_AVAILABLE_VIDEO_ASSETS")
if __name__=="__main__":main()
