#!/usr/bin/env python3
"""Original 58.5-second Windows+V animated walkthrough with Vietnamese neural narration.

EDITORIAL PREVIEW ONLY: UI illustrations are SIMULATED, not real screenshots.
Not for TikTok/Buffer automatic publication. Voice service rights must be checked
separately before using a neural voice in commercially distributed videos.
"""
from __future__ import annotations

import asyncio
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 30
DURATION = 58.5
SEGMENTS = [
    (6.5, "BẠN ĐÃ TỪNG MẤT ĐOẠN COPY?", "Bạn vừa sao chép đoạn mới, nhưng lại mất đoạn cũ? Đây là cách tìm lại ngay, không cần copy từ đầu."),
    (7.0, "PHÍM TẮT WINDOWS + V", "Trên Windows mười hoặc mười một, nhấn đồng thời phím Windows và chữ V. Một cửa sổ nhỏ sẽ hiện ra."),
    (7.0, "BẬT LỊCH SỬ BẢNG TẠM", "Nếu đây là lần đầu sử dụng, bạn hãy bấm nút Bật, để kích hoạt tính năng lịch sử bảng tạm trên máy tính."),
    (8.0, "BƯỚC 1: SAO CHÉP ĐOẠN ĐẦU", "Bây giờ, mở tài liệu. Bôi đen dòng thứ nhất, rồi nhấn Control C để sao chép. Tiếp theo là dòng thứ hai."),
    (7.5, "BƯỚC 2: COPY THÊM VÀI ĐOẠN", "Sao chép thêm dòng thứ ba. Windows vẫn lưu những đoạn trước đó. Bạn không cần quay lại từng trang để sao chép lại."),
    (8.0, "BƯỚC 3: CHỌN ĐOẠN CŨ", "Nhấn Windows và V thêm một lần. Danh sách các đoạn đã sao chép sẽ hiện ra. Bấm chọn đúng nội dung bạn cần."),
    (8.0, "KẾT QUẢ: DÁN THÀNH CÔNG", "Đoạn văn bản được dán vào đúng vị trí con trỏ. Như vậy, bạn lấy lại được nội dung cũ chỉ trong vài giây."),
    (6.5, "MẸO HAY NHƯNG CẦN AN TOÀN", "Đừng sao chép mật khẩu hoặc thông tin bí mật trên máy dùng chung. Hãy lưu video và theo dõi Góc Công Nghệ Tiện Ích nhé."),
]
assert abs(sum(x[0] for x in SEGMENTS) - DURATION) < 0.001
NAVY=(9,18,44); BLUE=(22,97,202); PURPLE=(118,57,198)
CYAN=(52,226,242); RED=(255,51,70); GOLD=(255,216,61)
WHITE=(246,251,255); PALE=(186,214,250); INK=(32,49,75)
FONT_B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def f(size,bold=False): return ImageFont.truetype(FONT_B if bold else FONT_R,size)
def rect(d,xy,fill,radius=14,outline=None,width=2):
    d.rounded_rectangle(xy,radius=radius,fill=fill,outline=outline,width=width)
def text(d,xy,t,size=26,color=WHITE,bold=False,anchor=None):
    d.text(xy,t,font=f(size,bold),fill=color,anchor=anchor,stroke_width=0)
def center(d,y,t,size=32,color=WHITE,bold=True):
    text(d,(W//2,y),t,size,color,bold,"ma")
def arrow(d,x,y,a,b,red=RED):
    d.line((x,y,a,b),fill=red,width=9)
    angle=math.atan2(b-y,a-x)
    tail=34
    d.polygon([(a,b),
       (a-tail*math.cos(angle-.35),b-tail*math.sin(angle-.35)),
       (a-tail*math.cos(angle+.35),b-tail*math.sin(angle+.35))],fill=red)

def label(d,words,x=70,y=915):
    # 2-3 short lines, all above the TikTok bottom UI safe strip
    for i,ln in enumerate(words):
        text(d,(x,y+i*46),ln,29,WHITE,True)

def background(scene):
    colors=[
        ((17,31,82),(101,35,138)), ((8,48,112),(13,96,154)),
        ((26,34,105),(81,42,145)), ((11,66,111),(33,61,145)),
        ((40,35,107),(6,126,135)), ((9,52,110),(96,40,143)),
        ((9,82,98),(29,90,139)), ((63,32,105),(13,79,118))
    ]
    top,bottom=colors[scene]
    image=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(image)
    for y in range(H):
        v=y/H
        d.line((0,y,W,y),fill=tuple(int(a*(1-v)+b*v) for a,b in zip(top,bottom)))
    for y in range(55,H,68):
        d.line((0,y,W,y),fill=(43,76,135),width=1)
    for x in range(0,W,68):
        d.line((x,0,x,H),fill=(39,70,128),width=1)
    rect(d,(32,28,688,98),(15,30,70),20,(69,160,220),2)
    d.ellipse((49,46,84,81),fill=CYAN)
    text(d,(96,46),"GÓC CÔNG NGHỆ TIỆN ÍCH",25,WHITE,True)
    rect(d,(46,124,670,199),(18,40,84),17,(61,166,231),2)
    center(d,148,SEGMENTS[scene][1],25,GOLD if scene in (0,7) else CYAN,True)
    return image

def note_window(d,lines=True):
    rect(d,(62,302,660,847),(232,241,252),26,(111,190,244),3)
    rect(d,(65,305,657,370),(206,222,243),21)
    d.rectangle((65,345,657,370),fill=(206,222,243))
    text(d,(87,325),"Tài liệu ghi chú",23,INK,True)
    for x,col in [(566,(82,199,156)),(595,(243,193,82)),(625,(248,100,103))]:
        d.ellipse((x,327,x+18,345),fill=col)
    d.line((78,375,641,375),fill=(153,182,218),width=3)
    if lines:
        for i,line in enumerate(["Báo cáo công việc","Kiểm tra thiết bị","Hoàn thành nhiệm vụ"]):
            text(d,(100,407+i*73),line,28,INK,False)
            d.line((100,448+i*73,608,448+i*73),fill=(182,200,224),width=1)

def history_window(d,enabled=True):
    rect(d,(80,298,637,851),(30,49,83),27,(89,182,246),3)
    rect(d,(100,319,618,381),(49,77,125),15)
    text(d,(129,337),"Lịch sử bảng tạm",27,WHITE,True)
    if enabled:
        for idx,line in enumerate(["Báo cáo công việc","Kiểm tra thiết bị","Hoàn thành nhiệm vụ"]):
            y=417+idx*104
            rect(d,(111,y,603,y+88),(217,233,251),18)
            text(d,(138,y+29),line,25,INK,True)
            text(d,(555,y+32),"⋯",22,INK,True)
        rect(d,(145,774,576,821),(47,101,146),14)
        center(d,793,"Bấm vào mục muốn dán",19,WHITE)
    else:
        center(d,425,"Chào mừng đến Clipboard",25,WHITE)
        center(d,487,"Kích hoạt để lưu nhiều đoạn",21,PALE)
        rect(d,(260,588,469,673),(46,148,237),19,(116,221,254),2)
        text(d,(366,618),"Bật",32,WHITE,True,"ma")

def illustrated(scene,phase):
    im=background(scene)
    d=ImageDraw.Draw(im)
    center(d,230,["BẠN ĐÃ GẶP TÌNH HUỐNG NÀY?","CHỈ CẦN HAI PHÍM",
       "LẦN ĐẦU THÌ BẤM BẬT","SAO CHÉP NHƯ BÌNH THƯỜNG",
       "MÁY TÍNH VẪN GHI NHỚ","MỞ LẠI LỊCH SỬ COPY",
       "ĐÃ DÁN ĐÚNG NỘI DUNG!","MẸO TIỆN NHƯNG AN TOÀN"][scene],28,WHITE,True)
    pulse=(phase%5)
    thick=6+2*(pulse%3)
    rect(d,(42,888,679,1009),(17,35,75),16,(88,181,231),2)
    if scene==0:
        note_window(d)
        rect(d,(91,472,588,523),(232,208,251),11)
        text(d,(105,479),"Đoạn B vừa sao chép",26,INK,True)
        rect(d,(87,391,489,457),None,12,RED,thick)
        arrow(d,597,557,474,459)
        label(d,["Copy đoạn mới...", "Đoạn cũ vẫn lấy lại được!"])
    elif scene==1:
        rect(d,(76,319,645,760),(23,49,96),31,(85,176,246),3)
        text(d,(112,346),"BÀN PHÍM  •  MÔ PHỎNG",21,PALE,True)
        for row in range(3):
            for col in range(5):
                x=102+105*col;y=410+101*row
                rect(d,(x,y,x+90,y+82),(70,99,157),13,(124,156,210),2)
        rect(d,(93,596,265,690),(38,160,226),17,RED,thick)
        text(d,(178,623),"WIN",36,WHITE,True,"ma")
        rect(d,(408,596,515,690),(154,90,223),17,RED,thick)
        text(d,(462,620),"V",44,WHITE,True,"ma")
        arrow(d,360+phase*3,350,453,590)
        label(d,["Nhấn cùng lúc:", "Windows + V"])
    elif scene==2:
        history_window(d,False)
        rect(d,(246,578,483,688),None,19,RED,thick)
        arrow(d,560,514,468,595)
        label(d,["Chọn nút được khoanh đỏ", "để bật lịch sử bảng tạm"])
    elif scene==3:
        note_window(d)
        rect(d,(96,400,489,451),(165,214,251),12,RED,thick)
        arrow(d,530,563,475,437)
        rect(d,(136,695,578,789),(34,105,164),20,(78,202,244),3)
        center(d,725,"CTRL  +  C",37,GOLD)
        label(d,["Bôi đen đoạn thứ nhất", "nhấn Control + C"])
    elif scene==4:
        note_window(d)
        chosen=1+(phase%2)
        for i in range(3):
            x=94;y=398+73*i
            if i==chosen:
                rect(d,(x,y,601,y+60),(176,230,244),12,RED,thick)
        arrow(d,573,680,479,405+chosen*73)
        rect(d,(158,695,563,786),(37,103,162),18,(97,210,242),3)
        text(d,(360,725),"CTRL  +  C",36,GOLD,True,"ma")
        label(d,["Copy thêm dòng hai, ba", "các đoạn cũ vẫn được lưu"])
    elif scene==5:
        history_window(d,True)
        rect(d,(102,513,611,618),None,15,RED,thick)
        arrow(d,622,412,568,535)
        label(d,["Windows + V lần nữa", "chọn đoạn cũ cần dán"])
    elif scene==6:
        note_window(d,False)
        text(d,(104,408),"Tài liệu tổng hợp",29,INK,True)
        rect(d,(98,512,608,596),(196,246,221),14,RED,thick)
        text(d,(118,527),"Kiểm tra thiết bị",30,(34,110,76),True)
        arrow(d,591,691,542,590)
        rect(d,(171,727,564,804),(26,130,115),19,(86,238,180),2)
        text(d,(365,752),"DÁN THÀNH CÔNG",24,WHITE,True,"ma")
        label(d,["Không phải quay lại tìm", "đoạn văn bản ban đầu!"])
    else:
        rect(d,(92,320,630,803),(34,49,96),29,(233,147,217),3)
        d.arc((279,350,439,555),180,360,fill=GOLD,width=17)
        rect(d,(263,474,459,629),GOLD,25)
        d.ellipse((342,533,383,574),fill=(29,46,87))
        d.rectangle((357,562,369,596),fill=(29,46,87))
        center(d,686,"ĐỪNG COPY MẬT KHẨU!",28,RED)
        center(d,743,"LƯU VIDEO • THEO DÕI KÊNH",23,CYAN)
        label(d,["Bảo vệ thông tin cá nhân", "và chia sẻ mẹo hữu ích"])
    # Brand and on-screen indicators
    rect(d,(46,1111,675,1150),(14,36,71),12)
    text(d,(64,1120),"MÀN HÌNH MÔ PHỎNG • BẢN XEM TRƯỚC",16,PALE,True)
    start=sum(v[0] for v in SEGMENTS[:scene])
    frac=(start+phase*SEGMENTS[scene][0]/5)/DURATION
    rect(d,(46,1167,674,1177),(52,79,123),5)
    rect(d,(46,1167,46+int(frac*628),1177),CYAN,5)
    text(d,(47,1201),f"{scene+1:02d} / 08",18,GOLD,True)
    return im

def command(args):
    subprocess.run(args,check=True,timeout=240,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def duration(path):
    return float(json.loads(subprocess.check_output(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)])
    )["format"]["duration"])

async def speak_scenes(root):
    for i,(_,_,narration) in enumerate(SEGMENTS):
        out=root/f"voice_{i}.mp3"
        error=None
        for attempt in range(3):
            try:
                await edge_tts.Communicate(narration,voice="vi-VN-NamMinhNeural",
                    rate="+8%",volume="+0%").save(str(out))
                if out.stat().st_size<5000:raise RuntimeError("TTS_FILE_TOO_SMALL")
                error=None
                break
            except Exception as exc:
                error=exc
                await asyncio.sleep(2+attempt)
        if error: raise RuntimeError(f"TTS_UNAVAILABLE_SCENE_{i}: {error}")
        print("VOICE_SCENE",i,"seconds",round(duration(out),2),"bytes",out.stat().st_size,flush=True)

def assemble_narration(root):
    chunks=[]
    total=0
    for i,(sec,_,_) in enumerate(SEGMENTS):
        inputfile=root/f"voice_{i}.mp3"
        actual=duration(inputfile)
        fit=sec-0.45
        factor=max(1.0,actual/fit)
        if factor>1.6:raise RuntimeError(f"NARRATION_TOO_FAST_SCENE_{i}_{factor:.2f}")
        output=root/f"voice_{i}.wav"
        command(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
             "-i",str(inputfile),"-af",f"atempo={factor:.4f},apad=pad_dur=3,atrim=duration={sec:.3f}",
             "-ac","1","-ar","48000","-c:a","pcm_s16le",str(output)])
        with wave.open(str(output)) as wav:
            nframes=wav.getnframes()
            data=np.frombuffer(wav.readframes(nframes),dtype="<i2").copy()
            if wav.getframerate()!=48000 or wav.getnchannels()!=1:raise RuntimeError("WRONG_AUDIO_FORMAT")
        length=round(sec*48000)
        if len(data)<length:data=np.pad(data,(0,length-len(data)))
        chunks.append(data[:length]);total+=length
        print("AUDIO_FIT",i,round(actual,2),"to",sec,"speed",round(factor,3),flush=True)
    final=np.concatenate(chunks)
    assert len(final)==round(DURATION*48000)
    target=root/"voice_track.wav"
    with wave.open(str(target),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(48000);out.writeframes(final.astype("<i2").tobytes())
    return target

def make_music(root):
    rate=48000
    n=round(DURATION*rate)
    t=np.arange(n,dtype=np.float32)/rate
    sound=np.zeros(n,dtype=np.float32)
    chords=[(174.61,220.0,261.63),(196,246.94,293.66),(164.81,220,261.63),(174.61,233.08,293.66),
            (196,246.94,329.63),(174.61,220,261.63),(164.81,196,261.63),(174.61,220,293.66)]
    offset=0
    for idx,(sec,_,_) in enumerate(SEGMENTS):
        starts=int(offset*rate);ends=min(n,round((offset+sec)*rate))
        local=np.arange(ends-starts,dtype=np.float32)/rate
        chord=chords[idx]
        pad=np.zeros(len(local),dtype=np.float32)
        for k,hz in enumerate(chord):
            pad+=.0045*np.sin(2*np.pi*hz*local+idx)*(1-.12*k)
        clip=pad
        for k in range(int(sec/.49)+1):
            s=int(k*.49*rate)
            if s>=len(local):break
            length=min(len(local)-s,int(.42*rate))
            tt=np.arange(length,dtype=np.float32)/rate
            hz=chord[k%3]*(2 if k%4==0 else 1)
            env=np.exp(-tt*12)*(1-np.exp(-tt*75))
            clip[s:s+length]+=.023*np.sin(2*np.pi*hz*tt)*env
        if idx>0:
            length=min(len(local),int(.23*rate))
            tt=np.arange(length,dtype=np.float32)/rate
            swoosh=.015*np.sin(2*np.pi*(360*tt+700*tt*tt))*np.exp(-tt*21)
            clip[:length]+=swoosh
        taper=np.minimum(1,np.minimum(local/.3,(sec-local)/.3))
        sound[starts:ends]+=clip*np.maximum(taper,0)
        offset+=sec
    sound*=np.minimum(1,np.minimum(t/.8,(DURATION-t)/.8))
    out=root/"original_music.wav"
    data=(np.clip(sound,-.5,.5)*32767).astype("<i2")
    with wave.open(str(out),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(data.tobytes())
    return out

def make_visual(root):
    ffconcat=root/"frames.ffconcat"
    entries=["ffconcat version 1.0"]
    for i,(sec,_,_) in enumerate(SEGMENTS):
        for phase in range(5):
            path=root/f"frame_{i}_{phase}.jpg"
            illustrated(i,phase).save(path,"JPEG",quality=91,subsampling=0)
            entries.append(f"file '{path}'")
            entries.append(f"duration {sec/5:.5f}")
    entries.append(f"file '{root / 'frame_7_4.jpg'}'")
    ffconcat.write_text("\n".join(entries)+"\n",encoding="utf8")
    return ffconcat

def main():
    out=Path("media-voice-preview/WINDOWS_V_58_GIAY_GIONG_VIET_NAM.mp4")
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tiktok-winv-58-") as td:
        d=Path(td)
        asyncio.run(speak_scenes(d))
        voice=assemble_narration(d)
        music=make_music(d)
        frames=make_visual(d)
        command(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(frames),
            "-i",str(voice),"-i",str(music),
            "-filter_complex",
            "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2:attack=12:release=100,volume=1.22[v];"
            "[2:a]volume=0.28[m];"
            "[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.92[a]",
            "-map","0:v","-map","[a]","-vf","fps=30,format=yuv420p",
            "-c:v","libx264","-preset","veryfast","-crf","23",
            "-c:a","aac","-b:a","160k","-ar","48000",
            "-t",str(DURATION),"-movflags","+faststart",str(out)])
    p=json.loads(subprocess.check_output(["ffprobe","-v","error",
            "-show_entries","format=duration,size:stream=codec_name,codec_type,width,height",
            "-of","json",str(out)]))
    kinds={s["codec_type"] for s in p["streams"]}
    if not {"audio","video"}.issubset(kinds):raise SystemExit("MISSING_VIDEO_OR_AUDIO")
    if abs(float(p["format"]["duration"])-DURATION)>.1:raise SystemExit("WRONG_DURATION")
    if int(p["format"]["size"])<500_000:raise SystemExit("BAD_VIDEO_SIZE")
    video=next(s for s in p["streams"] if s["codec_type"]=="video")
    if (video["width"],video["height"])!=(720,1280):raise SystemExit("WRONG_FRAME")
    metadata={
      "status":"AUDITION_ONLY_NOT_APPROVED_NOT_FOR_TIKTOK_AUTOPOST",
      "duration_seconds":DURATION,"source":"Original illustrated simulated Windows UI; not real screen capture",
      "narration":"Microsoft Edge neural Vietnamese NamMinh voice; generated for technical preview, commercial reuse permission not verified",
      "audio_original":"Original synthesized quiet musical bed; no third-party licensed music",
      "storyboard":"Eight scenes, animated true-red rectangles and arrows pointing to simulated UI targets",
      "output":str(out),"qa":p
    }
    (out.parent/(out.stem+".json")).write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n")
    print("WINDOWS_V_NEURAL_58S_PREVIEW_RENDERED",out,p["format"],flush=True)

if __name__=="__main__":main()
