#!/usr/bin/env python3
"""Render original professional 9:16 TikTok videos, keeping text in TikTok safe zones.

Source: media/100_video_scripts.json. No copyrighted music or third-party footage.
Never overwrite CN001: it is already published.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
LEFT, RIGHT = 85, 530
# Information stays within y=145..790. TikTok bottom text and right rail remain empty.
Y_MIN, Y_MAX = 145, 790
BG = (8, 18, 38)
WHITE = (241, 247, 255)
MUTED = (158, 183, 211)
CYAN = (61, 217, 246)
MINT = (79, 230, 185)
GOLD = (244, 190, 100)
DURATIONS = (3.0, 3.7, 3.7, 3.7, 2.7)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
REGULAR = FONT_DIR / "DejaVuSans.ttf"
BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else REGULAR), size)

def wrapped(draw, text, face, width):
    lines, current = [], ""
    for word in str(text).split():
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def fit(draw, text, width, lines_allowed, start=47, minimum=20):
    for size in range(start, minimum-1, -1):
        face = font(size, True)
        lines = wrapped(draw, text, face, width)
        if len(lines) <= lines_allowed and all(draw.textbbox((0,0), line, font=face)[2] <= width for line in lines):
            return face, lines
    raise ValueError("Text too long for safe area: " + str(text)[:100])

def palette(number):
    return (CYAN, MINT, GOLD)[(number-1) % 3]

def base(item, accent):
    frame = Image.new("RGB", (W,H), BG)
    draw = ImageDraw.Draw(frame)
    for y in range(H):
        t = y / H
        draw.line((0,y,W,y), fill=(int(8+5*t),int(18+13*t),int(38+15*t)))
    for x in range(0, W, 48):
        draw.line((x,0,x,H), fill=(24,39,61))
    for y in range(0, H, 48):
        draw.line((0,y,W,y), fill=(24,39,61))
    draw.rounded_rectangle((50,90,669,1165), radius=38, outline=(51,75,103), width=2)
    draw.rounded_rectangle((70,119,646,225), radius=25, fill=(20,43,67))
    draw.ellipse((88,153,117,182), fill=accent)
    draw.text((128,146), "GÓC CÔNG NGHỆ", font=font(23,True), fill=WHITE)
    draw.text((128,179), "TIỆN ÍCH  ·  MẸO HAY", font=font(17), fill=MUTED)
    draw.line((90,246,531,246), fill=accent, width=4)
    draw.rounded_rectangle((90,268,530,312),radius=15,fill=(27,53,79))
    draw.text((107,278), "#"+str(item["number"]).zfill(3),font=font(22,True),fill=accent)
    category = str(item.get("category") or "Công nghệ").upper()
    while draw.textbbox((0,0),category,font=font(18,True))[2] > 276:
        category = category[:-1]
    draw.text((233,281),category,font=font(18,True),fill=MUTED)
    # Decoration below TikTok captions; absolutely no instructional text.
    for i in range(6):
        yy = 955 + i*31
        draw.line((90, yy, 200+i*14, yy),fill=(29,66,92),width=3)
        draw.ellipse((199+i*14,yy-4,207+i*14,yy+4),fill=accent)
    return frame, draw

def scene(item, phase):
    accent = palette(int(item["number"]))
    frame, draw = base(item,accent)
    if phase == 0:
        draw.text((92,344), "MẸO CÔNG NGHỆ  ·  17 GIÂY", font=font(19,True),fill=accent)
        face, lines = fit(draw, item["title"], 435, 5, start=49, minimum=26)
        yy=401
        for line in lines:
            draw.text((90,yy),line,font=face,fill=WHITE)
            yy += face.size+13
        draw.rounded_rectangle((91,692,531,779),radius=22,fill=(23,48,72),outline=(51,95,125),width=2)
        draw.text((113,716),"3 BƯỚC NGẮN, DỄ LÀM",font=font(22,True),fill=WHITE)
        draw.text((113,751),"Xem tiếp để làm đúng",font=font(17),fill=MUTED)
    elif phase in (1,2,3):
        idx=phase-1
        draw.text((91,345),"BƯỚC "+str(phase).zfill(2)+" / 03",font=font(28,True),fill=accent)
        draw.rounded_rectangle((86,401,537,783),radius=27,fill=(22,44,71),outline=(50,85,117),width=2)
        face, lines = fit(draw,item["steps"][idx], 382, 7, start=39, minimum=20)
        lineheight=face.size+12
        yy=max(427,int(588 - len(lines)*lineheight/2))
        if yy+len(lines)*lineheight>731: yy=731-len(lines)*lineheight
        if yy<418: raise ValueError("Too much text for panel")
        for line in lines:
            draw.text((111,yy),line,font=face,fill=WHITE)
            yy += lineheight
        for k in range(3):
            x=106 + k*141
            draw.rounded_rectangle((x,745,x+117,754),radius=5,fill=accent if k<=idx else (52,78,106))
    elif phase == 4:
        draw.text((90,370),"ĐÃ BIẾT CÁCH LÀM?",font=font(33,True),fill=WHITE)
        draw.rounded_rectangle((88,500,533,669),radius=26,fill=(20,53,76),outline=accent,width=3)
        draw.text((114,528),"LƯU VIDEO",font=font(43,True),fill=accent)
        draw.text((114,590),"Theo dõi để xem thêm",font=font(22,True),fill=WHITE)
        draw.text((114,627),"mẹo công nghệ hữu ích",font=font(20),fill=MUTED)
        draw.text((92,752),"@goccongnghetienich",font=font(20,True),fill=MUTED)
    else:
        raise ValueError("Unknown slide")
    return frame

def render(item, path):
    with tempfile.TemporaryDirectory(prefix="tiktok-safe-") as td:
        folder=Path(td)
        images=[]
        for i in range(5):
            out=folder/(str(i)+".png")
            scene(item,i).save(out,optimize=True)
            images.append(out)
        filelist=folder/"sequence.ffconcat"
        entries=["ffconcat version 1.0"]
        for i,img in enumerate(images):
            entries.extend(["file '"+str(img)+"'","duration "+str(DURATIONS[i])])
        entries.append("file '"+str(images[-1])+"'")
        filelist.write_text("\n".join(entries)+"\n",encoding="utf-8")
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(filelist),
            "-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","28",
            "-movflags","+faststart","-t",str(sum(DURATIONS)),str(path)],check=True)
        probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
            "stream=width,height,r_frame_rate","-show_entries","format=duration,size","-of","json",str(path)]))
        stream=(probe.get("streams") or [{}])[0]
        if (stream.get("width"),stream.get("height"),stream.get("r_frame_rate"))!=(720,1280,"30/1"):
            raise RuntimeError("Invalid MP4 dimensions/framerate: "+str(path))
        if not (15 <= float(probe["format"]["duration"]) <= 19):
            raise RuntimeError("Invalid MP4 duration: "+str(path))
        if int(probe["format"]["size"]) < 40000:
            raise RuntimeError("Video unexpectedly small: "+str(path))
        print("RENDER_OK",item["id"],probe["format"]["size"], flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--start",type=int,default=2)
    parser.add_argument("--end",type=int,default=100)
    args=parser.parse_args()
    if not 2<=args.start<=args.end<=100:
        raise SystemExit("Only unpublished CN002-CN100 may be replaced")
    src=Path("media/100_video_scripts.json")
    items=json.loads(src.read_text(encoding="utf-8"))
    if len(items)!=100 or [x.get("id") for x in items]!=["CN"+str(i).zfill(3) for i in range(1,101)]:
        raise SystemExit("Manifest sequence invalid")
    for item in items[args.start-1:args.end]:
        if len(item.get("steps",[]))!=3:
            raise ValueError("Expected 3 steps in "+item["id"])
        render(item,Path("media")/(item["id"]+".mp4"))
    print("BATCH_RENDERED",args.start,args.end,flush=True)

if __name__=="__main__":
    main()
