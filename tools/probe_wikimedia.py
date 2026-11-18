#!/usr/bin/env python3
import json,urllib.request,urllib.parse
files=[
"Cellular 5G Equipment - Cell Tower Antennas.jpg",
"Referee during a football match.jpg",
"Rice terraces of Lim Mong valley seen from a paraglider, Mu Cang Chai.jpg",
"Bun cha Hanoi.jpg",
"Rice terraces in Sapa, Vietnam.jpg",
]
for name in files:
 query={"action":"query","titles":"File:"+name,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1080","format":"json"}
 url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(query)
 req=urllib.request.Request(url,headers={"User-Agent":"GocCongNgheTienIchEditorial/1.0 (licensed file attribution audit; github repository)"})
 try:
  with urllib.request.urlopen(req,timeout=25) as res: data=json.load(res)
  page=next(iter(data["query"]["pages"].values()))
  info=(page.get("imageinfo") or [{}])[0]
  meta=info.get("extmetadata") or {}
  print("IMAGE_METADATA",name,"PAGE",page.get("pageid"),"URL",str(info.get("thumburl") or info.get("url"))[:175],"LICENSE",str((meta.get("LicenseShortName") or {}).get("value"))[:80],flush=True)
  media=info.get("thumburl") or info.get("url")
  if media:
   rq=urllib.request.Request(media,headers={"User-Agent":"GocCongNgheTienIchEditorial/1.0 (licensed media research)"})
   with urllib.request.urlopen(rq,timeout=30) as rr:
    buf=rr.read(6000000)
    print("IMAGE_BYTES",name,rr.status,len(buf),"CTYPE",rr.headers.get("Content-Type"),flush=True)
 except Exception as exc:
  print("IMAGE_ERROR",name,type(exc).__name__,str(exc)[:90],flush=True)
