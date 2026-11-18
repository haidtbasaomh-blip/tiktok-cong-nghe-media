#!/usr/bin/env python3
"""Produce one ORIGINAL short-form nature video from truly moving Commons footage.

- This is not a vlog or a first-hand claim.
- No watermarks are removed; no influencer videos are downloaded.
- Every clip must have a verified Commons metadata license and source page.
- A real camera clip is used, not a generated still.
- Copyright and editorial manual acceptance remains REQUIRED before publication.
"""
from __future__ import annotations
import datetime as dt
import hashlib, html, json, os, re, shutil, subprocess, tempfile, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

OUT=Path("media-editorial")
ID="WD001"
TARGET=OUT/(ID+".mp4")
RIGHTS=OUT/(ID+".json")
CLIPS=[
  {"title":"File:Video of the waterfall of Seythenex.ogv",
   "expected_license":"Public domain",
   "caption":"Một dòng nước, nhiều nhịp chảy"},
  {"title":"File:Saut de l'Ognon.ogv",
   "expected_license":"Public domain",
   "caption":"Mỗi thác lại có hình dáng khác nhau"},
  {"title":"File:Schraubenfall Hintertux.webm",
   "expected_license":"CC BY 4.0",
   "caption":"Bạn muốn khám phá dòng thác nào?"}
]
HEADLINE="3 THÁC NƯỚC – 3 GÓC NHÌN"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
UA={"User-Agent":"GocCongNgheTienIch-OriginalVideo/1.0 (creative-commons footage remixed with recorded attributions)"}
ACCEPTED_LICENSES={"CC0","Public domain","CC BY 4.0"}
MAX_DOWNLOAD=25_000_000

def compact(s):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",s or ""))).strip()

def downloaded(url, limit=MAX_DOWNLOAD):
    if urllib.parse.urlsplit(url).scheme!="https":
        raise RuntimeError("INVALID_SOURCE_NOT_HTTPS")
    req=urllib.request.Request(url,headers=UA)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=55) as res:
                if res.status!=200 or not res.geturl().startswith("https://"):
                    raise RuntimeError("SOURCE_REDIRECT_UNSAFE")
                raw=res.read(limit+1)
                if len(raw)>limit:raise RuntimeError("SOURCE_TOO_LARGE")
                return raw
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,503) or attempt==3:
                raise
            try:
                delay=int(exc.headers.get("Retry-After") or "0")
            except (TypeError,ValueError):
                delay=0
            delay=max(8,min(90,delay)) if delay else (8,18,35)[attempt]
            print("WIKIMEDIA_RATE_LIMIT_RESPECT_RETRY_AFTER",delay,"SECONDS",flush=True)
            time.sleep(delay)
    raise RuntimeError("SOURCE_RETRY_EXHAUSTED")

def resolve_cc(title, expected):
    params={"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|mime|size|extmetadata","format":"json"}
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    page=next(iter(json.loads(downloaded(url,900000))["query"]["pages"].values()))
    info=(page.get("imageinfo") or [None])[0]
    if not info:raise RuntimeError("NO_VIDEO_MEDIA "+title)
    meta=info.get("extmetadata") or {}
    lic=compact((meta.get("LicenseShortName") or {}).get("value"))
    artist=compact((meta.get("Artist") or {}).get("value"))[:140]
    credit=compact((meta.get("Credit") or {}).get("value"))[:180]
    licurl=compact((meta.get("LicenseUrl") or {}).get("value"))
    if lic not in ACCEPTED_LICENSES or lic!=expected:
        raise RuntimeError("LICENSE_MISMATCH:"+title+":"+lic)
    if lic=="CC BY 4.0" and (not artist or licurl!="https://creativecommons.org/licenses/by/4.0/"):
        raise RuntimeError("LICENSE_ATTRIBUTION_MISSING")
    mime=str(info.get("mime") or "")
    if "video/" not in mime and "ogg" not in mime:raise RuntimeError("NOT_A_VIDEO_CLIP")
    if not str(info.get("url") or "").startswith("https://"):raise RuntimeError("INSECURE_MEDIA_URL")
    if not 100_000 < int(info.get("size") or 0) < MAX_DOWNLOAD:
        raise RuntimeError("MEDIA_SIZE_UNSAFE")
    return {"page_url":"https://commons.wikimedia.org/wiki/"+title.replace(" ","_"),
            "origin_media_url":info["url"],"creator":artist or "not provided by source",
            "credit":credit,"license":lic,"license_url":licurl,
            "mime":mime,"filename":title,"checked_utc":dt.datetime.now(dt.timezone.utc).isoformat()}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def ffprobe(path):
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)],timeout=40))
    v=next((x for x in data.get("streams",[]) if x.get("codec_type")=="video"),{})
    a=next((x for x in data.get("streams",[]) if x.get("codec_type")=="audio"),{})
    return {"width":int(v.get("width") or 0),"height":int(v.get("height") or 0),
            "duration":float((data.get("format") or {}).get("duration") or 0),
            "fps":v.get("avg_frame_rate"),"audio":bool(a)}

def create_segment(source,out,caption,seconds):
    # Original overlay: restrained typography, footage remains visible,
    # wide footage kept entirely in a clear center window with soft blurred fill.
    filtertext=(
      "[0:v]fps=25,split=2[b][f];"
      "[b]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
      "boxblur=12:2,eq=brightness=-0.16:saturation=0.75[bg];"
      "[f]scale=700:890:force_original_aspect_ratio=decrease,setsar=1[fg];"
      "[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,"
      "drawtext=fontfile='"+FONT+"':textfile='"+str(out.parent/"headline.txt")+"':"
      "fontsize=32:fontcolor=white:x=(w-text_w)/2:y=100:"
      "box=1:boxcolor=black@0.55:boxborderw=15,"
      "drawtext=fontfile='"+FONT+"':textfile='"+str(out.parent/"caption.txt")+"':"
      "fontsize=29:fontcolor=white:x=(w-text_w)/2:y=1030:"
      "box=1:boxcolor=black@0.60:boxborderw=16,"
      "fade=t=in:st=0:d=0.4,fade=t=out:st="+str(seconds-0.4)+":d=0.4,"
      "format=yuv420p[v]"
    )
    (out.parent/"headline.txt").write_text(HEADLINE,encoding="utf8")
    (out.parent/"caption.txt").write_text(caption,encoding="utf8")
    # Original soft ambient soundtrack synthesized from filtered colored noise;
    # explicitly NOT presented as on-location sound or a real water recording.
    cmd=["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
         "-stream_loop","-1","-i",str(source),
         "-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.018:sample_rate=44100",
         "-filter_complex",filtertext+";[1:a]highpass=f=100,lowpass=f=1500,"
                            "afade=t=in:st=0:d=0.3,afade=t=out:st="
                            +str(seconds-0.4)+":d=0.4[a]",
         "-map","[v]","-map","[a]","-t",str(seconds),
         "-c:v","libx264","-preset","veryfast","-crf","23","-r","25",
         "-c:a","aac","-b:a","96k","-movflags","+faststart",str(out)]
    subprocess.run(cmd,check=True,timeout=180)

def render():
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wd-tiktok-") as folder:
        work=Path(folder)
        meta=[];segments=[]
        for idx,item in enumerate(CLIPS,1):
            receipt=resolve_cc(item["title"],item["expected_license"])
            raw=downloaded(receipt["origin_media_url"])
            suffix=Path(urllib.parse.urlsplit(receipt["origin_media_url"]).path).suffix or ".webm"
            src=work/f"source{idx}{suffix}"
            src.write_bytes(raw)
            receipt["source_sha256"]=sha(raw)
            specs=ffprobe(src)
            receipt["source_specs"]=specs
            if min(specs["width"],specs["height"])<240 or specs["duration"]<3.0:
                raise RuntimeError("LOW_QUALITY_SOURCE "+str(item["title"]))
            segment=work/f"scene{idx}.mp4"
            create_segment(src,segment,item["caption"],9.0)
            if not segment.is_file() or segment.stat().st_size<120_000:
                raise RuntimeError("SEGMENT_OUTPUT_INVALID")
            segments.append(segment)
            meta.append(receipt)
            print("VERIFIED_REAL_VIDEO",idx,item["title"],"LICENSE",receipt["license"],
                  "SOURCE_SIZE",len(raw),"VIDEO_SPEC",specs,flush=True)
        listfile=work/"scenes.txt"
        listfile.write_text("".join("file '"+str(f)+"'\n" for f in segments),encoding="utf8")
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
          "-f","concat","-safe","0","-i",str(listfile),
          "-c","copy","-movflags","+faststart",str(TARGET)],
           check=True,timeout=95)
        outspec=ffprobe(TARGET)
        if not (26.3<outspec["duration"]<28 and outspec["width"]==720
                and outspec["height"]==1280 and outspec["audio"]):
            raise RuntimeError("OUTPUT_QA_SPEC_FAILED:"+str(outspec))
        checksum=hashlib.sha256(TARGET.read_bytes()).hexdigest()
        manifest={
          "id":ID,"topic":"Ba thác nước qua những cảnh quay thật có giấy phép",
          "purpose":"Original short scenic montage and commentary prompts",
          "format":"licensed_camera_footage_documentary_preview",
          "no_firsthand_travel_claim":True,
          "human_first_idea":True,
          "licensed_camera_video_scene_count":len(meta),
          "video_file":str(TARGET),"duration":outspec["duration"],
          "resolution":"720x1280","video_codec":"H.264",
          "audio":"Original synthetic filtered-noise ambience, not real-location audio, no third-party music",
          "publication_status":"ARCHIVED_NOT_PUBLISHED_NEEDS_HUMAN_RIGHTS_AND_CREATIVE_REVIEW",
          "upload_to_buffer_or_tiktok":False,
          "full_original_captions":["Một dòng nước, nhiều nhịp chảy",
                                    "Mỗi thác lại có hình dáng khác nhau",
                                    "Bạn muốn khám phá dòng thác nào?"],
          "source_video_rights":meta,
          "rights_and_credit_must_be_in_final_public_caption":True,
          "content_needs_human_final_visual_audio_qa":True,
          "video_sha256":checksum,
          "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat()
        }
        RIGHTS.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        preview=OUT/(ID+"-preview.jpg")
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
         "-ss","3","-i",str(TARGET),"-frames:v","1","-q:v","2",str(preview)],
         check=True,timeout=60)
        print("VIDEO_SAMPLE_READY_NOT_PUBLISHED",str(TARGET),"BYTES",TARGET.stat().st_size,
            "DURATION",outspec["duration"],"SHA256",checksum,flush=True)

if __name__=="__main__":
    render()
