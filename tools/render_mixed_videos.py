#!/usr/bin/env python3
"""Six licensed, visually animated, original Vietnamese 30-second vertical videos.
Never uploads to TikTok. Source photos come only from Wikimedia Commons API,
after exact licence verification. Original video assembly, typography, overlays,
storyboard, sound design; author and license recorded in JSON and final scene.
"""
from __future__ import annotations
import argparse,hashlib,html,json,math,os,re,subprocess,tempfile,time,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps

W,H=720,1280
import imageio_ffmpeg
FFMPEG=os.environ.get("FFMPEG_BIN") or imageio_ffmpeg.get_ffmpeg_exe()
SCRIPT=Path("series/multi_topic_batch01.json")
OUT=Path("media-mixed")
FONT_ROOT=Path("/usr/share/fonts/truetype/dejavu")
FONT_BOLD=str(FONT_ROOT/"DejaVuSans-Bold.ttf")
FONT_REG=str(FONT_ROOT/"DejaVuSans.ttf")
LICENSE_MAP={
    "CC0":"https://creativecommons.org/publicdomain/zero/1.0/",
    "CC BY 2.0":"https://creativecommons.org/licenses/by/2.0/",
    "CC BY-SA 4.0":"https://creativecommons.org/licenses/by-sa/4.0/",
}
ART={
 "MX001":("Cellular 5G Equipment - Cell Tower Antennas.jpg","CC BY 2.0"),
 "MX002":("Referee during a football match.jpg","CC0"),
 "MX003":("Rice terraces of Lim Mong valley seen from a paraglider, Mu Cang Chai.jpg","CC BY-SA 4.0"),
 "MX004":("Bun cha Hanoi.jpg","CC BY-SA 4.0"),
 "MX006":("Rice terraces in Sapa, Vietnam.jpg","CC0"),
}
DURATIONS=[4.4,6.5,6.5,6.5,6.1] # exactly 30 seconds
def font(size,bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG,size)

def compact(text):
    text=html.unescape(re.sub("<[^>]*>","",text or ""))
    return re.sub(r"\s+"," ",text).strip()

def validated_photo(vid):
    if vid not in ART:
        return None,None
    name,expected=ART[vid]
    query=urllib.parse.urlencode({"action":"query","titles":"File:"+name,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1280","format":"json"})
    url="https://commons.wikimedia.org/w/api.php?"+query
    header={"User-Agent":"GocCongNgheTienIchEditorial/1.0 (original educational Vietnamese video; licensing attribution)"}
    with urllib.request.urlopen(urllib.request.Request(url,headers=header),timeout=30) as rsp:
        data=json.load(rsp)
    p=next(iter(data["query"]["pages"].values()))
    if "imageinfo" not in p:raise RuntimeError("Missing Commons source "+name)
    info=p["imageinfo"][0];meta=info.get("extmetadata") or {}
    license_name=compact((meta.get("LicenseShortName") or {}).get("value"))
    if license_name!=expected:raise RuntimeError("License mismatch "+name+": "+license_name+" != "+expected)
    link=info.get("thumburl") or info["url"]
    if urllib.parse.urlsplit(link).scheme!="https":raise RuntimeError("Insecure media source")
    with urllib.request.urlopen(urllib.request.Request(link,headers=header),timeout=45) as rsp:
        if "image/" not in rsp.headers.get("Content-Type",""):raise RuntimeError("Nonimage source")
        raw=rsp.read(6000000)
    if not (25000<len(raw)<6000000):raise RuntimeError("Unexpected source image size")
    from io import BytesIO
    photo=ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert("RGB")
    if min(photo.size)<380:raise RuntimeError("Photo too small")
    credit=compact((meta.get("Artist") or {}).get("value"))[:95] or "Wikimedia Commons"
    attribution={
        "creator":credit,
        "original_file":name,
        "license":license_name,
        "license_url":LICENSE_MAP[license_name],
        "source_url":"https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_"),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "source_type":"Wikimedia Commons; image is background illustration, not live news footage",
        "source_checked_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
    }
    return photo,attribution

def vertical_photo(src,z=1.0,offset=0):
    if src is None:
        img=Image.new("RGB",(W,H),(17,29,53))
        d=ImageDraw.Draw(img)
        for y in range(H):
            r=int(10+y/H*14);g=int(25+y/H*20);b=int(56+y/H*8)
            d.line((0,y,W,y),fill=(r,g,b))
        return img
    target_ratio=W/H
    w,h=src.size
    cropw,croph=(w, w/target_ratio) if (w/h)>target_ratio else (h*target_ratio,h)
    cropw/=z;croph/=z
    left=(w-cropw)*(.5+offset*.32)
    top=(h-croph)*(.5+offset*.14)
    left=max(0,min(w-cropw,left));top=max(0,min(h-croph,top))
    image=src.crop((round(left),round(top),round(left+cropw),round(top+croph)))
    return image.resize((W,H),Image.Resampling.LANCZOS)

def hexrgb(s):
    return tuple(int(s[i:i+2],16) for i in (1,3,5))

def wrap(draw,text,f,maxwidth,limit=4):
    parts=[];line=""
    for word in str(text).split():
        trial=(line+" "+word).strip()
        if draw.textbbox((0,0),trial,font=f)[2]<=maxwidth:
            line=trial
        else:
            if line:parts.append(line)
            line=word
    if line:parts.append(line)
    return parts[:limit]

def textblock(d,txt,x,y,width,size,spacing=13,fill=(255,255,255),bold=True,maxlines=4):
    for fs in range(size,21,-1):
        f=font(fs,bold); lines=wrap(d,txt,f,width,limit=100)
        if len(lines)<=maxlines:break
    for ln in lines:
        d.text((x+2,y+2),ln,font=f,fill=(0,0,0),stroke_width=1,stroke_fill=(0,0,0))
        d.text((x,y),ln,font=f,fill=fill)
        y+=fs+spacing
    return y

def overlay_frame(src,entry,idx,progress,credit):
    rgb=vertical_photo(src,1.08+progress*.10,(idx%2*2-1)*(.55-progress*.35))
    blur=rgb.filter(ImageFilter.GaussianBlur(6))
    frame=Image.blend(rgb,blur,0.25)
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    c=hexrgb(entry["color"])
    # Darkened panels guarantee readability without covering the entire photo
    d.rectangle((0,0,W,105),fill=(5,12,23,215))
    d.rounded_rectangle((24,116,568,202),radius=23,fill=(7,19,36,219))
    d.rectangle((0,270,586,900),fill=(3,12,29,155))
    d.rectangle((0,960,W,H),fill=(4,12,23,185))
    # Brand tag, category bar and animated progress
    d.ellipse((38,135,85,182),fill=c)
    d.text((53,145),"G",font=font(27,True),fill=(6,15,25))
    d.text((99,136),"GÓC CÔNG NGHỆ TIỆN ÍCH",font=font(20,True),fill=(255,255,255))
    d.text((99,167),entry["pillar"].upper(),font=font(18,True),fill=c)
    d.rounded_rectangle((22,224,558,235),radius=5,fill=(42,58,76))
    d.rounded_rectangle((22,224,22+int(536*(idx+progress)/5),235),radius=5,fill=c)
    # Moving accent pulse
    phase=math.sin(progress*math.pi)
    d.ellipse((500+int(phase*12),270,538+int(phase*12),308),fill=c)
    # All key text in left safe area, no lower TikTok caption overlap
    if idx==0:
        d.text((34,310),"BẠN CÓ BIẾT?",font=font(29,True),fill=c)
        textblock(d,entry["hook"],36,404,500,49,17,(255,255,255),maxlines=5)
        d.rounded_rectangle((35,745,544,829),radius=23,fill=(*c,230))
        d.text((54,769),"XEM 3 ĐIỀU THÚ VỊ",font=font(23,True),fill=(5,16,28))
    elif idx in (1,2,3):
        d.text((38,307),f"ĐIỀU {idx:02d} / 03",font=font(34,True),fill=c)
        fact=entry["facts"][idx-1]
        textblock(d,fact,36,420,510,41,16,(255,255,255),maxlines=6)
        d.rounded_rectangle((38,736,526,810),radius=19,outline=(*c,255),width=3)
        d.text((56,758),"HIỂU ĐÚNG • XEM TIẾP",font=font(21,True),fill=(255,255,255))
    else:
        d.text((36,330),"BẠN NGHĨ SAO?",font=font(37,True),fill=c)
        textblock(d,entry["close"],36,443,514,42,15,(255,255,255),maxlines=4)
        d.rounded_rectangle((35,736,530,815),radius=21,fill=(*c,220))
        d.text((50,760),"THEO DÕI KÊNH NHÉ!",font=font(23,True),fill=(4,16,23))
    # Original graphics (not actual footage claim); persistent short ID
    d.text((42,1000),entry["id"]+"  •  VIDEO MINH HỌA",font=font(18,True),fill=(235,243,250))
    if idx==4 and credit:
        d.text((42,1035),"Ảnh: "+credit["creator"][:41],font=font(15),fill=(222,234,248))
        d.text((42,1060),"Wikimedia · "+credit["license"]+" · Đã biên tập",font=font(15),fill=(222,234,248))
    if idx==4 and not credit:
        d.text((42,1035),"Đồ họa nguyên bản · Không sử dụng clip bên thứ ba",font=font(15),fill=(222,234,248))
    # Simple kinetic motif for society topic, original visual
    if src is None:
        r=80+int(55*math.sin(progress*math.pi))
        d.ellipse((445-r,575-r,445+r,575+r),outline=(*c,150),width=7)
        d.ellipse((445-55,575-55,445+55,575+55),outline=(*c,220),width=8)
        d.text((418,548),"?",font=font(52,True),fill=(255,255,255))
    return Image.alpha_composite(frame.convert("RGBA"),layer).convert("RGB")

def render(entry,mode):
    vid=entry["id"]
    image,rights=validated_photo(vid)
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mx-clip-") as dirname:
        folder=Path(dirname)
        # Animated zoom/pan of an authentic licensed image + original typography
        # 5 scenes * 6 fps. Encoded via FFmpeg to 24 fps for smooth playback.
        framecount=0
        for scene,seconds in enumerate(DURATIONS):
            n=round(seconds*6)
            for k in range(n):
                progress=k/max(1,n-1)
                frame=overlay_frame(image,entry,scene,progress,rights)
                frame.save(folder/(f"f{framecount:04d}.jpg"),quality=88,subsampling=0)
                framecount+=1
        target=OUT/(vid+".mp4")
        source=str(folder/"f%04d.jpg")
        audio="sine=frequency=392:sample_rate=44100:duration=30"
        # The original low-volume synth bed is generated mathematically by FFmpeg,
        # not a recording of copyrighted music.
        args=[FFMPEG,"-hide_banner","-nostdin","-loglevel","error","-y",
              "-framerate","6","-i",source,"-f","lavfi","-i",audio,
              "-filter_complex","[0:v]fps=24,format=yuv420p[v];[1:a]volume=0.018,afade=t=in:st=0:d=0.4,afade=t=out:st=29:d=1[a]",
              "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","25",
              "-c:a","aac","-b:a","64k","-movflags","+faststart","-t","30",str(target)]
        subprocess.run(args,check=True,timeout=240)
        if target.stat().st_size<100000: raise RuntimeError("MP4 too small "+vid)
        metadata={
            "video_id":vid,"title":entry["title"],"topic":entry["pillar"],
            "video_file":str(target),"seconds":30,"resolution":"720x1280","fps":24,
            "source_story_url":entry["source"],
            "original_script":entry["facts"],"image_rights":rights,
            "audio":"Original synthesized tone from ffmpeg lavfi sine; no third-party music",
            "visual_edit":"Original typographic video scenes with photo motion, tinted gradients, animated progress",
            "license_note":("CC BY-SA 4.0: derivative video share-alike applies to graphical adaptation; attribution in video and accompanying JSON." if rights and rights["license"]=="CC BY-SA 4.0" else "Original visuals with attribution as required."),
            "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "publication_status":"ARCHIVED_NOT_PUBLISHED"
        }
        (OUT/(vid+".json")).write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("RENDERED_MIXED_VIDEO:",vid,"SIZE:",target.stat().st_size,"SECONDS:30","LICENSE:",rights["license"] if rights else "Original",flush=True)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--id",required=True)
    args=parser.parse_args()
    entries=json.loads(SCRIPT.read_text(encoding="utf-8"))["items"]
    found=[e for e in entries if e["id"]==args.id]
    if len(found)!=1:raise SystemExit("Exactly one valid MX source ID required")
    render(found[0],args.id)
if __name__=="__main__":
    main()
