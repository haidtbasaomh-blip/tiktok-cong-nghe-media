#!/usr/bin/env python3
"""Make a vertical pilot using real NASA/ISS camera time-lapses and original Vietnamese narration.

Never publishes. Requires separate manual fact, rights, voice, visual and audio signoffs.
Does not use other TikTok/YouTube creators' footage.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import math
import subprocess
import ssl
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

PILOT=Path("series/nasa_real_footage_pilot.json")
OUT=Path("media-editorial")
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MODEL="vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx"
VOICE_REPO="rhasspy/piper-voices"

def shell(args,**kw):
    return subprocess.run(args,check=True,timeout=300,**kw)

def file_sha(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()

def probe(path):
    r=shell(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],capture_output=True,text=True)
    data=json.loads(r.stdout)
    video=next((s for s in data["streams"] if s.get("codec_type")=="video"),{})
    audio=next((s for s in data["streams"] if s.get("codec_type")=="audio"),None)
    return {"seconds":round(float(data["format"]["duration"]),2),
            "width":int(video.get("width") or 0),"height":int(video.get("height") or 0),
            "fps":video.get("avg_frame_rate"),"audio":bool(audio)}

def download_video(item,dest):
    url=item["media_url"]
    if not (url.startswith("https://svs.gsfc.nasa.gov/vis/") or url.startswith("https://images-assets.nasa.gov/video/")):
        raise ValueError("UNAPPROVED_SOURCE_DOMAIN")
    request=urllib.request.Request(url,headers={"User-Agent":"GocCongNgheTienIch/1.0 source-licensed educational film"})
    import certifi
    try:
        trusted=ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request,timeout=60,context=trusted) as reply:
            if reply.status!=200 or not (reply.geturl().startswith("https://svs.gsfc.nasa.gov/") or reply.geturl().startswith("https://images-assets.nasa.gov/")):
                raise RuntimeError("NASA_SOURCE_REDIRECT_FAILED")
            raw=reply.read(27_000_000)
        if not 300_000 < len(raw) < 27_000_000:
            raise RuntimeError("NASA_CLIP_INVALID_OR_TOO_LARGE")
        dest.write_bytes(raw)
    except (urllib.error.URLError,ssl.SSLError) as exc:
        print("TRY_VERIFIED_OS_CA_CURL_FALLBACK",type(exc).__name__,flush=True)
        # Curl uses OS-trusted CA store; it does NOT disable TLS verification.
        shell(["curl","--fail","--location","--silent","--show-error",
               "--proto","=https","--proto-redir","=https",
               "--connect-timeout","25","--max-time","120",
               "--max-filesize","27000000",
               "--output",str(dest),url],capture_output=True,text=True)
    if not dest.is_file() or not 300_000 < dest.stat().st_size < 27_000_000:
        raise RuntimeError("NASA_CLIP_MISSING_OR_TOO_LARGE")
    with dest.open("rb") as stream:
        signature=stream.read(12)
    if not (signature[:4]==bytes.fromhex("1a45dfa3") or signature[4:8]==b"ftyp"):
        raise RuntimeError("NOT_VALID_MP4_OR_WEBM_CONTAINER")
    p=probe(dest)
    if p["width"]<640 or p["height"]<360 or p["seconds"]<15:
        raise RuntimeError("NASA_CLIP_TOO_SHORT_OR_LOW_QUALITY")
    return {**item,"sha256":file_sha(dest),"downloaded_bytes":len(raw),"probe":p}

def voice_to_wav(data,work):
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as ex:
        raise SystemExit("INSTALL_HUGGINGFACE_HUB") from ex
    path=hf_hub_download(repo_id=VOICE_REPO,filename=MODEL)
    config=hf_hub_download(repo_id=VOICE_REPO,filename=MODEL+".json")
    if not Path(config).is_file() or not Path(path).is_file():
        raise RuntimeError("VOICE_MODEL_MISSING")
    target=work/"narration.wav"
    # Piper runs locally; no unofficial Microsoft Edge service or paid API.
    shell(["python","-m","piper","-m",str(path),"-f",str(target),
           "--",data["narration"]],capture_output=True,text=True)
    info=probe(target)
    seconds=info["seconds"]
    if not 16 < seconds < 48 or not info["audio"] or target.stat().st_size < 100_000:
        raise RuntimeError("NARRATION_INVALID_DURATION_OR_AUDIO")
    return target, info

def make_scene(source, dest, textfile, seconds, offset):
    # Retain actual widescreen time-lapse footage, with soft video-based fill.
    # Do not place artificial footage or faces.
    f=(
       "[0:v]fps=25,split=2[a][b];"
       "[a]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
       "boxblur=luma_radius=15:luma_power=2,eq=brightness=-0.22[bg];"
       "[b]scale=700:750:force_original_aspect_ratio=decrease,setsar=1[fg];"
       "[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,"
       "drawbox=x=0:y=0:w=720:h=200:color=black@0.35:t=fill,"
       "drawtext=fontfile="+FONT+":text='GÓC CÔNG NGHỆ TIỆN ÍCH':"
       "fontsize=24:fontcolor=white:x=35:y=71,"
       "drawtext=fontfile="+FONT+":textfile="+str(textfile)+":"
       "fontsize=28:fontcolor=white:x=(w-text_w)/2:y=1040:"
       "box=1:boxcolor=black@0.60:boxborderw=18,"
       "drawtext=fontfile="+FONT+":text='TƯ LIỆU NASA / ISS':"
       "fontsize=18:fontcolor=white:x=35:y=1185,"
       "format=yuv420p[v]"
    )
    shell(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
           "-ss",str(offset),"-stream_loop","-1","-i",str(source),
           "-t",str(seconds),"-filter_complex",f,"-map","[v]","-an",
           "-c:v","libx264","-preset","veryfast","-crf","24",
           "-r","25","-movflags","+faststart",str(dest)])
    if dest.stat().st_size<80_000:raise RuntimeError("RENDERED_SCENE_TOO_SMALL")

def main():
    data=json.loads(PILOT.read_text(encoding="utf8"))
    if data["video_id"]!="NASA001" or len(data["captions"])!=5 or len(data["sources"])!=2:
        raise SystemExit("INVALID_OR_UNREVIEWED_PILOT_CONFIGURATION")
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tiktok-nasa-") as temp:
        work=Path(temp)
        paths={}
        rights=[]
        for index,item in enumerate(data["sources"],1):
            clip=work/("source"+str(index)+"."+item.get("format","webm"))
            rights.append(download_video(item,clip))
            paths[item["id"]]=clip
            print("REAL_CAMERA_CLIP_ACQUIRED",item["id"],rights[-1]["downloaded_bytes"],flush=True)
        narration, ainfo=voice_to_wav(data,work)
        # Honor account editorial maximum if speech is longer than expected.
        duration=math.ceil(ainfo["seconds"]+1.1)
        if not 24<=duration<=40:
            raise RuntimeError("NARRATION_TIMING_NEEDS_EDITING:"+str(duration))
        segments=[]
        original_shots=[("iss_earth",0),("iss_other",8),("iss_earth",15),
                        ("iss_other",22),("iss_earth",32)]
        per_scene=duration/5
        for i,(clip_id,offset) in enumerate(original_shots):
            cap=work/("cap"+str(i)+".txt")
            cap.write_text(data["captions"][i],encoding="utf8")
            part=work/("scene"+str(i)+".mp4")
            make_scene(paths[clip_id],part,cap,per_scene,offset)
            segments.append(part)
        playlist=work/"scenes.txt"
        playlist.write_text("".join("file '"+str(p)+"'\n" for p in segments),encoding="utf8")
        visuals=work/"visuals.mp4"
        shell(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
               "-f","concat","-safe","0","-i",str(playlist),"-c","copy",str(visuals)])
        output=OUT/"NASA001.mp4"
        shell(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
               "-i",str(visuals),"-i",str(narration),"-map","0:v:0","-map","1:a:0",
               "-c:v","copy","-c:a","aac","-ar","44100","-b:a","128k",
               "-af","loudnorm=I=-18:TP=-2:LRA=7,apad","-t",str(duration),
               "-movflags","+faststart",str(output)])
        spec=probe(output)
        if not (spec["width"]==720 and spec["height"]==1280 and spec["audio"]
                and 24<=spec["seconds"]<=41):
            raise RuntimeError("FINAL_VERTICAL_AUDIO_QA_FAILED:"+str(spec))
        frame=OUT/"NASA001-preview.jpg"
        shell(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
              "-ss","3.0","-i",str(output),"-frames:v","1","-q:v","2",str(frame)])
        report={
          "video_id":data["video_id"],"title":data["title"],"file":str(output),
          "video_sha256":file_sha(output),"duration_seconds":spec["seconds"],
          "resolution":"720x1280","shots":5,
          "footage":"NASA ISS real Earth-observation footage from 2 original source assets, 5 edited shots",
          "narration":"Vietnamese offline Piper TTS voice, source script authored for this channel",
          "voice_model":data["voice"],"narration_duration":ainfo["seconds"],
          "source_video_credits":rights,"accuracy_sources":data["accuracy_sources"],
          "source_audio_reused":False,"source_music_reused":False,
          "no_firsthand_claim":True,
          "requires_human_audio_visual_rights_fact_review":True,
          "approved_for_publication":False,
          "status":"PILOT_ARCHIVED_NOT_POSTED",
          "generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat()
        }
        (OUT/"NASA001.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print("REAL_VIDEO_WITH_VIETNAMESE_NARRATION_CREATED",
              output,"SECONDS",spec["seconds"],"BYTES",output.stat().st_size,
              "NOT_POSTED",flush=True)
if __name__=="__main__":
    main()
