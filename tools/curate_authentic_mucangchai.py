#!/usr/bin/env python3
"""Curate authentic Mu Cang Chai imagery via Wikimedia Commons license metadata.

This is a research-only action: no uploads to TikTok, no claim of copyright
ownership, and no publication approvals. Store image source/artist/license
and SHA256. Avoid Wikimedia derivatives with unclear licensing.
"""
from __future__ import annotations
import html, json, hashlib, re, urllib.parse, urllib.request, os, time
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont

OUT=Path("series/authentic_mucangchai")
OUT.mkdir(parents=True,exist_ok=True)
TERMS=["Mu Cang Chai rice terraces","Mù Cang Chải terraces","Mu Cang Chai Vietnam"]
ALLOWED={"CC0","CC BY 2.0","CC BY 3.0","CC BY 4.0","CC BY-SA 4.0"}
UA={"User-Agent":"GocCongNgheTienIchResearch/1.0 (licensed Wikimedia content for educational Vietnam travel video)"}
def text(s):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>","",s or ""))).strip()
def request(url,limit=4500000):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=30) as r:
        if r.status!=200 or not r.geturl().startswith("https://"):
            raise RuntimeError("Unsafe source or failed download")
        return r.read(limit)
def search(term):
    params={"action":"query","generator":"search","gsrsearch":term,
      "gsrnamespace":"6","gsrlimit":"50","prop":"imageinfo",
      "iiprop":"url|size|extmetadata","iiurlwidth":"960","format":"json"}
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    data=json.loads(request(url,1200000))
    return [v for v in (data.get("query",{}).get("pages",{}) or {}).values() if v.get("imageinfo")]
def main():
    records={}
    for term in TERMS:
        try:
            pages=search(term)
            print("SEARCH",term,"PAGES",len(pages),flush=True)
        except Exception as exc:
            print("SEARCH_ERROR",term,type(exc).__name__,flush=True)
            continue
        for page in pages:
            title=page.get("title","");info=page["imageinfo"][0]
            name=title.removeprefix("File:")
            if re.search(r"\.(gif|svg|pdf|png|tiff|webm|ogg)$",name,re.I):continue
            if any(key in name.lower() for key in ("logo","map","test","poster","banner","diagram","illustration","icon")):continue
            if "mu" not in name.lower() and "mù" not in name.lower():continue
            licence=text((info.get("extmetadata",{}).get("LicenseShortName") or {}).get("value"))
            if licence not in ALLOWED:continue
            width=int(info.get("width",0));height=int(info.get("height",0))
            if min(width,height)<650:continue
            src=info.get("thumburl") or info.get("url")
            if not src or not urllib.parse.urlparse(src).scheme=="https":continue
            records[title]={"title":title,"license":licence,"width":width,"height":height,"image_url":src,
                "page":"https://commons.wikimedia.org/wiki/"+title.replace(" ","_"),
                "artist":text((info.get("extmetadata",{}).get("Artist") or {}).get("value"))[:130] or "Wikimedia Commons",
                "license_url":text((info.get("extmetadata",{}).get("LicenseUrl") or {}).get("value"))}
    # Prefer unique, license-cleared, high-res actual terrace photos.
    rank=lambda x:(x["license"]=="CC0",x["license"].startswith("CC BY "),x["width"]*x["height"])
    candidates=sorted(records.values(),key=rank,reverse=True)
    chosen=[]
    for c in candidates:
        if len(chosen)>=9:break
        try:
            data=request(c["image_url"],4000000)
            if len(data)<20000 or len(data)>3999999:continue
            im=ImageOps.exif_transpose(Image.open(BytesIO(data))).convert("RGB")
            if min(im.size)<500:continue
            c.update({"sha256":hashlib.sha256(data).hexdigest(),"downloaded_size":len(data),"preview_file":f"ref{len(chosen)+1:02d}.jpg",
                      "license_checked_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())})
            im.thumbnail((620,850))
            im.save(OUT/c["preview_file"],quality=87)
            chosen.append(c)
        except Exception as exc:
            print("IMAGE_ERROR",c["title"],type(exc).__name__,flush=True)
    (OUT/"candidates.json").write_text(json.dumps({
       "subject":"Authentic photographic imagery of Mu Cang Chai terraces",
       "research_only":True,
       "visual_review_required_before_publication":True,
       "photos":chosen},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if len(chosen)<4:raise SystemExit("NOT_ENOUGH_LICENSED_PHOTOGRAPHS")
    print("AUTHENTIC_LICENSED_PHOTOS_ACQUIRED",len(chosen),flush=True)
    for c in chosen:print("PHOTO",c["preview_file"],c["license"],c["title"],flush=True)
if __name__=="__main__":
    main()
