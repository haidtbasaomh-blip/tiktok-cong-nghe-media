#!/usr/bin/env python3
"""Build an original photo-essay from five real photographs already in this repo.

The photos depict actual Mu Cang Chai landscapes and carry per-image
Wikimedia/CC licences. This is NOT real moving camera footage or a vlog.
No source creator's video or watermark is used. Never auto-publish.
"""
from __future__ import annotations
import datetime as dt, hashlib, html, json, math, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT=Path("series/authentic_mucangchai")
OUTPUT=Path("media-editorial")
NAME="MC001"
W,H=720,1280
FPS=12
SECONDS=28
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCENE_CAPTIONS=["TÂY BẮC TỪ MỘT GÓC KHÁC",
                "Những đường ruộng theo sườn núi",
                "Màu vàng đổi theo mùa vụ",
                "Một vùng đất, nhiều góc nhìn",
                "Giữ nét đẹp của núi rừng"]
DURATIONS=[5.6,5.6,5.6,5.6,5.6]
def font(size,bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT,size)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def frame(photo,text,idx,phase):
    # Real source photographs remain the visible foreground. Their soft motion
    # is an editorial Ken Burns effect, never represented as real camera motion.
    bg=ImageOps.fit(photo,(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.5))
    bg=bg.filter(ImageFilter.GaussianBlur(16)).convert("RGB")
    mask=Image.new("RGBA",(W,H),(3,11,16,130))
    base=Image.alpha_composite(bg.convert("RGBA"),mask)
    # Preserve more of the original landscape in the foreground.
    maxw,maxh=650,890
    fw,fh=photo.size
    scale=min(maxw/fw,maxh/fh)
    nw,nh=round(fw*scale),round(fh*scale)
    nw,nh=max(1,nw),max(1,nh)
    picture=photo.resize((nw,nh),Image.Resampling.LANCZOS).convert("RGBA")
    # gentle zoom applied to the photograph, not pretending footage
    zoom=1.0+0.055*phase
    neww,newh=round(picture.width*zoom),round(picture.height*zoom)
    scaled=picture.resize((neww,newh),Image.Resampling.LANCZOS)
    left=max(0,(neww-picture.width)//2+round((phase-.5)*9*(1 if idx%2 else -1)))
    top=max(0,(newh-picture.height)//2)
    picture=scaled.crop((left,top,left+nw,top+nh))
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    cardx=(W-nw)//2
    cardy=236+(890-nh)//2
    d.rounded_rectangle((cardx-4,cardy-4,cardx+nw+4,cardy+nh+4),radius=26,fill=(255,255,255,35))
    overlay.alpha_composite(picture,(cardx,cardy))
    # Small header and a short one-line takeaway; never blocks the scene.
    d=ImageDraw.Draw(overlay)
    d.text((34,56),"GÓC CÔNG NGHỆ TIỆN ÍCH",font=font(23,True),fill=(235,246,250,255))
    d.rounded_rectangle((32,119,352,172),radius=18,fill=(3,23,22,185))
    d.text((49,132),"KHÁM PHÁ TÂY BẮC",font=font(21,True),fill=(153,235,206,255))
    d.rounded_rectangle((27,1104,690,1190),radius=18,fill=(2,16,24,200))
    f=font(28,True)
    while d.textbbox((0,0),text,font=f)[2]>605:
        f=font(f.size-1,True)
    d.text(((W-d.textbbox((0,0),text,font=f)[2])/2,1130),text,font=f,fill=(250,250,250,255))
    d.text((35,1225),"ẢNH THẬT ĐƯỢC CẤP PHÉP • VIDEO ẢNH KỂ CHUYỆN",font=font(13),fill=(231,240,242,240))
    # A low-key progress cue
    d.rounded_rectangle((35,1200,685,1207),radius=3,fill=(255,255,255,70))
    d.rounded_rectangle((35,1200,35+round(650*(idx+phase)/5),1207),radius=3,fill=(160,240,201,255))
    return Image.alpha_composite(base,overlay).convert("RGB")

def main():
    source=json.loads((ROOT/"candidates.json").read_text(encoding="utf8"))
    photos=source.get("photos",[])
    if len(photos)<5:raise RuntimeError("NEED_FIVE_ALREADY_VERIFIED_REAL_PHOTOS")
    files=[];rights=[]
    for i,p in enumerate(photos[:5]):
        path=ROOT/p["preview_file"]
        if not path.exists():raise RuntimeError("MISSING_ARCHIVED_REAL_IMAGE:"+str(path))
        with Image.open(path) as im:
            im.verify()
        if p.get("license") not in ("CC0","CC BY-SA 4.0"):
            raise RuntimeError("UNEXPECTED_PHOTO_LICENSE")
        if p["license"]=="CC BY-SA 4.0" and not p.get("artist"):
            raise RuntimeError("MISSING_AUTHOR_FOR_CC_BY_SA")
        rights.append({"image":str(path),"page":p["page"],"creator":p.get("artist"),
                       "license":p["license"],"license_url":p.get("license_url"),
                       "preview_derivative_sha256":sha(path),
                       "source_image_sha256_recorded_at_research":p.get("sha256")})
        files.append(path)
    OUTPUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tiktok-cc-photoessay-") as tmp:
        folder=Path(tmp);count=0
        for idx,path in enumerate(files):
            photo=Image.open(path).convert("RGB")
            for t in range(round(FPS*DURATIONS[idx])):
                pct=t/max(1,round(FPS*DURATIONS[idx])-1)
                img=frame(photo,SCENE_CAPTIONS[idx],idx,pct)
                img.save(folder/f"frame{count:04d}.jpg",quality=85,subsampling=0)
                count+=1
        out=OUTPUT/(NAME+".mp4")
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
           "-framerate",str(FPS),"-i",str(folder/"frame%04d.jpg"),
           "-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.01:sample_rate=44100",
           "-vf","fps=25,format=yuv420p",
           "-af","lowpass=f=1300,afade=t=in:st=0:d=1,afade=t=out:st=27:d=1",
           "-c:v","libx264","-preset","veryfast","-crf","24","-r","25",
           "-c:a","aac","-b:a","64k","-movflags","+faststart","-t",str(SECONDS),str(out)],
          check=True,timeout=300)
        if out.stat().st_size<180000:raise RuntimeError("VIDEO_TOO_SMALL")
        proc=subprocess.run(["ffprobe","-v","error","-of","json","-show_streams","-show_format",str(out)],capture_output=True,text=True,check=True)
        probe=json.loads(proc.stdout)
        seconds=float(probe["format"]["duration"])
        video=next(x for x in probe["streams"] if x["codec_type"]=="video")
        if not (27<seconds<29 and video["width"]==720 and video["height"]==1280):
            raise RuntimeError("VIDEO_EXPORT_SPEC_FAILED")
        # Render five distinct preview frames into one contact sheet.
        sheet=Image.new("RGB",(5*250,450),(10,24,30))
        for i in range(5):
            src=ROOT/("ref"+str(i+1).zfill(2)+".jpg")
            im=Image.open(src).convert("RGB")
            im=ImageOps.fit(im,(250,450),method=Image.Resampling.LANCZOS)
            sheet.paste(im,(i*250,0))
        sheet.save(OUTPUT/(NAME+"-preview.jpg"),quality=88)
        metadata={
          "video_id":NAME,"title":"Mù Cang Chải qua năm khung hình thật",
          "type":"photo_essay_from_real_cc_photographs",
          "no_actual_camera_motion_claim":True,
          "no_fake_vlog_claim":True,
          "duration_seconds":round(seconds,2),"video_file":str(out),
          "video_sha256":sha(out),
          "licensed_image_sources":rights,
          "audio":"original synthesized subtle ambience, NOT a real location recording",
          "creative_notes":"Five real locations photos; Ken Burns, no unlicensed source videos; needs natural narration and human review",
          "derivative_sharealike_note":"CC BY-SA 4.0 images incorporated: any adapted material based on those images needs compliant attribution and sharealike licensing; review before distribution.",
          "publication_status":"ARCHIVED_NOT_PUBLISHED",
          "passes_automated_technical_export":True,
          "passes_manual_editorial_review":False,
          "approved_for_buffer":False,
          "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat()
        }
        (OUTPUT/(NAME+".json")).write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print("REAL_PHOTOESSAY_ARCHIVED",NAME,"DURATION",seconds,
              "SIZE_BYTES",out.stat().st_size,"SOURCES",len(rights),"NOT_POSTED",flush=True)
if __name__=="__main__":
    main()
