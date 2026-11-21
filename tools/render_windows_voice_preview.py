#!/usr/bin/env python3
"""Render an AUDIO-FOCUSED sample of Northern Vietnamese TTS over original simulated Windows+V graphics.
This is NOT a real Windows capture, full tutorial, rights-cleared commercial publication or TikTok post.
"""
from __future__ import annotations
import math, wave, json, argparse, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 15
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAVY = (10, 18, 47)
SKY = (32, 213, 247)
YELLOW = (255, 220, 64)
RED = (255, 68, 94)
GREEN = (31, 207, 131)
WHITE = (247, 251, 255)
TIMES = None

def f(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

def center(draw, y, txt, size, color, bold=False):
    font=f(size,bold)
    box=draw.textbbox((0,0),txt,font=font)
    draw.text(((W-(box[2]-box[0]))/2,y),txt,font=font,fill=color)

def multi(draw, x, y, txt, size=27, gap=16, color=WHITE, bold=False):
    for line in txt.split("\n"):
        draw.text((x,y),line,font=f(size,bold),fill=color)
        y+=size+gap

def gradient_bg():
    im=Image.new("RGB",(W,H),NAVY)
    d=ImageDraw.Draw(im)
    for y in range(H):
        mix=y/H
        d.line((0,y,W,y),fill=(int(9+13*mix),int(18+17*mix),int(47+48*mix)))
    for ix in range(-100,900,90):
        d.line((ix,0,ix+150,1280),fill=(29,45,92),width=1)
    for y in range(55,H,88):
        d.line((0,y,W,y),fill=(25,40,78),width=1)
    return im

def arrow(draw, x, y, tx, ty, colour=RED):
    draw.line((x,y,tx,ty),fill=colour,width=9)
    ang=math.atan2(ty-y,tx-x)
    pts=[(tx,ty),
         (tx-33*math.cos(ang)+14*math.sin(ang),ty-33*math.sin(ang)-14*math.cos(ang)),
         (tx-33*math.cos(ang)-14*math.sin(ang),ty-33*math.sin(ang)+14*math.cos(ang))]
    draw.polygon(pts,fill=colour)

def window(draw,caption="Notepad  •  mô phỏng"):
    draw.rounded_rectangle((51,313,670,955),radius=30,fill=(232,241,250),outline=(112,181,242),width=3)
    draw.rounded_rectangle((53,313,668,385),radius=26,fill=(226,234,244))
    draw.rectangle((53,362,668,385),fill=(226,234,244))
    draw.text((80,332),caption,font=f(24,True),fill=(35,56,92))
    for ix,color in enumerate(((250,105,111),(245,194,96),(89,212,161))):
        draw.ellipse((567+29*ix,341,585+29*ix,359),fill=color)
    draw.line((66,386,653,386),fill=(160,182,208),width=2)
    draw.text((82,410),"Báo cáo công việc",font=f(25),fill=(47,66,92))
    draw.text((82,457),"Kiểm tra thiết bị",font=f(25),fill=(47,66,92))
    draw.text((82,504),"Hoàn thành nhiệm vụ",font=f(25),fill=(47,66,92))
    draw.line((83,571,634,571),fill=(182,198,221),width=2)
    draw.text((82,607),"Nội dung đang soạn:",font=f(23),fill=(102,122,148))

def frame(base,sec,duration):
    im=base.copy()
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((27,30,690,113),radius=26,fill=(32,52,97),outline=(66,117,178),width=2)
    d.ellipse((49,55,89,95),fill=SKY)
    d.text((100,45),"GÓC CÔNG NGHỆ TIỆN ÍCH",font=f(25,True),fill=WHITE)
    d.text((100,79),"BẢN NGHE THỬ GIỌNG BẮC",font=f(17),fill=(162,212,243))
    d.rounded_rectangle((44,156,674,209),radius=13,fill=(43,79,142))
    d.text((64,170),"WINDOWS + V  ·  LỊCH SỬ COPY",font=f(24,True),fill=YELLOW)
    b1,b2,b3=duration*.25,duration*.56,duration*.80
    phase=0 if sec<b1 else 1 if sec<b2 else 2 if sec<b3 else 3
    accent=[SKY,YELLOW,(160,122,255),GREEN][phase]
    titles=["COPY NHIỀU ĐOẠN?","NHẤN WINDOWS + V","CHỌN ĐOẠN CŨ","DÁN LẠI NGAY!"]
    center(d,236,titles[phase],36,accent,True)
    window(d)
    glow=3+int(abs(math.sin(sec*5))*4)
    if phase==0:
        d.rounded_rectangle((69,398,480,543),radius=14,outline=RED,width=glow+2)
        d.rounded_rectangle((77,419,439,449),radius=6,fill=(167,220,255))
        arrow(d,545,670,440,524)
        d.text((101,699),"Đã copy nhiều đoạn",font=f(24,True),fill=(35,57,83))
        d.text((101,743),"Làm sao tìm đoạn cũ?",font=f(22),fill=(86,108,136))
    elif phase==1:
        # Original keyboard illustration, not an actual Windows screenshot.
        d.rounded_rectangle((76,617,645,849),radius=24,fill=(38,55,88))
        for row in range(2):
            for col in range(6):
                x=96+87*col;y=634+91*row
                d.rounded_rectangle((x,y,x+76,y+76),radius=13,fill=(92,111,151),outline=(132,158,194),width=2)
        d.rounded_rectangle((94,724,226,807),radius=16,fill=(44,187,223),outline=RED,width=glow+3)
        d.text((120,739),"WIN",font=f(28,True),fill=(8,27,60))
        d.rounded_rectangle((433,725,523,808),radius=15,fill=YELLOW,outline=RED,width=glow+3)
        d.text((462,739),"V",font=f(37,True),fill=(17,33,57))
        arrow(d,350,585,478,728)
        d.text((126,871),"Bấm đồng thời hai phím",font=f(23,True),fill=(41,66,98))
    elif phase==2:
        d.rounded_rectangle((98,551,623,851),radius=24,fill=(39,57,88),outline=SKY,width=3)
        d.text((122,568),"Lịch sử bảng tạm",font=f(26,True),fill=WHITE)
        for i,txt in enumerate(["Báo cáo công việc","Kiểm tra thiết bị","Hoàn thành nhiệm vụ"]):
            y=617+i*74
            d.rounded_rectangle((119,y,598,y+61),radius=13,fill=((224,238,251) if i==0 else (156,178,210)))
            d.text((142,y+13),txt,font=f(23),fill=(32,49,78))
            if i==0:d.rounded_rectangle((114,y-5,602,y+66),radius=16,outline=RED,width=glow+2)
        arrow(d,610,465,550,648)
    else:
        d.rounded_rectangle((73,643,560,709),radius=13,fill=(216,251,235),outline=GREEN,width=3)
        d.text((100,660),"Báo cáo công việc",font=f(28,True),fill=(28,91,69))
        d.rounded_rectangle((68,636,567,716),radius=18,outline=RED,width=glow+2)
        arrow(d,589,782,487,691)
        d.ellipse((299,802,399,902),fill=GREEN)
        d.line((327,855,351,878,383,826),fill=WHITE,width=10)
    d.rounded_rectangle((45,987,675,1101),radius=20,fill=(21,42,81),outline=(58,112,184),width=2)
    subtitles=[
        "Bạn vừa copy nhiều\nđoạn văn bản?",
        "Nhấn Windows + V\nđể mở lịch sử",
        "Chọn lại nội dung cũ\nbạn muốn dùng",
        "Dán lại ngay vào tài liệu\nkhông cần sao chép lần nữa"
    ]
    for index,line in enumerate(subtitles[phase].split("\n")):
        center(d,1001+index*40,line,26,WHITE,True)
    d.text((48,1128),"GIAO DIỆN MÔ PHỎNG • CHỈ ĐỂ NGHE THỬ",font=f(18),fill=(171,197,223))
    d.rounded_rectangle((50,1196,672,1206),radius=5,fill=(57,84,122))
    d.rounded_rectangle((50,1196,50+int(622*min(1,sec/duration)),1206),radius=5,fill=SKY)
    return im

def soundtrack(output, seconds):
    """Original soft tech plucks; entirely self-generated, no stock music."""
    rate=32000
    n=int(seconds*rate)
    track=np.zeros(n,dtype=np.float32)
    notes=[261.63,329.63,392.0,523.25,392,329.63,293.66,349.23,440,587.33,440,349.23]
    interval=.43
    for i in range(int(seconds/interval)+1):
        start=int(i*interval*rate)
        if start>=n:break
        count=min(int(.49*rate),n-start)
        t=np.arange(count,dtype=np.float32)/rate
        freq=notes[i%len(notes)]/2
        env=(1-np.exp(-t*110))*np.exp(-t*7)
        pluck=(np.sin(2*np.pi*freq*t)+.23*np.sin(2*np.pi*freq*2*t))*env
        track[start:start+count]+=.052*pluck
    # very subtle stereo atmosphere, no voice masking
    track += .004*np.sin(2*np.pi*120*np.arange(n)/rate).astype(np.float32)
    fade=np.minimum(1,np.minimum(np.arange(n)/(.35*rate),(n-np.arange(n))/(1*rate)))
    track *= np.maximum(fade,0)
    pcm=(np.clip(track,-.85,.85)*32767).astype("<i2")
    with wave.open(str(output),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm.tobytes())

def run(cmd):
    subprocess.run(cmd,check=True,timeout=150)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--voice",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    voice=Path(args.voice);out=Path(args.output)
    if voice.stat().st_size<50_000:raise SystemExit("VOICE_ASSET_TOO_SMALL")
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(voice)]))
    voice_duration=float(meta["format"]["duration"])
    if not 5<voice_duration<27:raise SystemExit("VOICE_DURATION_UNEXPECTED")
    duration=round(max(voice_duration+1.35,11.5),2)
    out.parent.mkdir(parents=True,exist_ok=True)
    base=gradient_bg()
    with tempfile.TemporaryDirectory(prefix="windows-v-voice-") as td:
        d=Path(td)
        frame_n=math.ceil(duration*FPS)
        for i in range(frame_n):
            frame(base,i/FPS,duration).save(d/f"f{i:04d}.jpg",quality=88,subsampling=1)
        soundtrack(d/"music.wav",duration)
        run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
          "-framerate",str(FPS),"-i",str(d/"f%04d.jpg"),"-i",str(voice),"-i",str(d/"music.wav"),
          "-filter_complex",
          "[1:a]aresample=48000,highpass=f=80,volume=1.05,apad=pad_dur=2[voice];"
          "[2:a]aresample=48000,volume=0.5[music];"
          "[voice][music]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.93[a]",
          "-map","0:v","-map","[a]","-vf","fps=30,format=yuv420p",
          "-c:v","libx264","-preset","veryfast","-crf","24",
          "-c:a","aac","-b:a","160k","-ar","48000","-t",str(duration),
          "-movflags","+faststart",str(out)])
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height","-of","json",str(out)]))
    kinds={t["codec_type"] for t in info["streams"]}
    if not {"video","audio"}.issubset(kinds):raise SystemExit("OUTPUT_MISSING_AUDIO_OR_VIDEO")
    if abs(float(info["format"]["duration"])-duration)>0.5:raise SystemExit("OUTPUT_DURATION_MISMATCH")
    if int(info["format"]["size"])<200_000:raise SystemExit("VIDEO_TOO_SMALL")
    print("PREVIEW_VOICE_AND_VIDEO_OK",str(out),"seconds",duration,"bytes",info["format"]["size"],"voice_seconds",voice_duration)

if __name__=="__main__":
    main()
