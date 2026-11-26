#!/usr/bin/env python3
"""Complete audio for three existing 58s real Windows demo review files.
Separate review exports only. Never alters old MP4s or approval/publisher state.
"""
import hashlib,json,math,re,subprocess as sp
from pathlib import Path
import numpy as np
import soundfile as sf
from vieneu import Vieneu
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"review/batch-01"
OUT=BASE/"voice-completed-20261126"
WORK=ROOT/"work/batch01-voice"
RATE=48000
TOTAL=58
VOICE="Anh Khôi"
SPEC=[
 ("WIN11_03_STARTUP_APPS","WIN11_03_STARTUP_APPS_58_GIAY_QUAY_THAT.mp4","dce712d67200c55178ac2640e555b37ce9f8cbe6",
  "https://support.microsoft.com/en-us/windows/experience/startup-boot/configure-startup-applications-in-windows",[
   (0,6,"Vừa vào máy đã có nhiều ứng dụng tự mở? Kiểm tra mục khởi động trước nhé."),
   (6,16,"Nhấn Control, Shift và Escape cùng lúc để mở Task Manager."),
   (16,28,"Chọn Startup apps. Xem cột trạng thái và mức ảnh hưởng khi khởi động. Đừng tắt vội ứng dụng bạn chưa nhận ra."),
   (28,45,"Chọn ứng dụng cá nhân không cần tự mở, rồi chọn Disable. Giữ nguyên phần mềm bảo mật, trình điều khiển và công cụ cơ quan nếu chưa rõ chức năng."),
   (45,58,"Khi trạng thái là Disabled, ứng dụng không tự chạy ở lần đăng nhập sau. Muốn bật lại, chọn Enable. Bạn vẫn mở ứng dụng bằng tay bình thường.")]),
 ("WIN11_04_SNIPPING_TOOL","WIN11_04_SNIPPING_TOOL_58_GIAY_QUAY_THAT.mp4","f814eb9dad10295b4a43d963d1184c0a6a0a88a6",
  "https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots",[
   (0,7,"Cần gửi ảnh một lỗi máy tính? Đừng chụp cả màn hình nếu chỉ cần một vùng nhỏ."),
   (7,18,"Nhấn phím Windows, Shift và chữ ét. Chọn chế độ hình chữ nhật trên thanh công cụ."),
   (18,31,"Kéo chuột quanh phần muốn chụp. Nhớ để đủ tiêu đề và nội dung lỗi, nhưng bỏ những thông tin không cần thiết."),
   (31,46,"Ảnh được đưa vào bảng tạm. Bạn có thể dán bằng Control V, hoặc mở thông báo của Snipping Tool để kiểm tra rồi lưu."),
   (46,58,"Trước khi gửi, kiểm tra lại ảnh. Không để lộ tên người dùng, số hồ sơ hay thông tin riêng. Chỉ gửi đúng phần người nhận cần xem.")]),
 ("WIN11_05_STORAGE_TEMPORARY_FILES","WIN11_05_STORAGE_TEMPORARY_FILES_58_GIAY_QUAY_THAT.mp4","ce0c3781ab9006787b389fe369d2b54fdfe0c253",
  "https://support.microsoft.com/en-us/windows/experience/storage-filemanagement/storage-settings-in-windows",[
   (0,7,"Ổ C sắp đầy? Hãy kiểm tra mục nào chiếm nhiều dung lượng trước khi xóa."),
   (7,18,"Mở Settings, vào System, rồi chọn Storage. Chờ Windows tính xong dung lượng."),
   (18,31,"Nhìn các nhóm chiếm nhiều chỗ. Mở Temporary files để xem danh sách tệp tạm và dung lượng từng mục."),
   (31,46,"Đọc kỹ từng mô tả. Bỏ chọn Downloads nếu chưa kiểm tra thư mục đó. Xem cả Thùng rác và tổng dung lượng đã chọn trước khi dọn."),
   (46,58,"Đừng xóa ngay nếu chưa chắc dữ liệu nào cần giữ. Trên máy cơ quan, làm theo quy định lưu trữ trước khi bật chế độ tự dọn.")])
]
def require(ok,why):
    if not ok:raise RuntimeError(why)
def run(*args):sp.run([str(a) for a in args],check=True)
def probe(p):
    return json.loads(sp.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)]))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gitblob(p):
    return sp.check_output(["git","hash-object",str(p)],cwd=ROOT,text=True).strip()
def video_md5(p):
    s=sp.check_output(["ffmpeg","-v","error","-i",str(p),"-map","0:v:0","-c","copy","-f","md5","-"],text=True).strip()
    require(re.fullmatch(r"MD5=[0-9a-f]{32}",s) is not None,"VIDEO_PACKET_HASH_UNAVAILABLE")
    return s
def db(rms):return 20*math.log10(max(1e-10,float(rms)))
def rms(a):return float(np.sqrt(np.mean(np.square(a,dtype=np.float64))))
def stamp(s):
    return f"00:00:{s:02d},000"
def music_bed():
    # Entirely original low-volume synthesized notes. No third-party song.
    track=np.zeros(TOTAL*RATE,dtype=np.float32)
    for i,start in enumerate(np.arange(0,TOTAL,.75)):
        ix=round(start*RATE)
        grid=np.arange(min(round(.6*RATE),len(track)-ix),dtype=np.float64)/RATE
        f=[130.81,164.81,196.0,261.63,146.83,196.0,220.0,293.66][i%8]
        note=.009*np.sin(2*np.pi*f*grid)*np.exp(-grid*7)*np.minimum(grid/.045,1)
        track[ix:ix+len(grid)]+=note.astype(np.float32)
    return track
def main():
    OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    inputs=[]
    for key,file,blob,source,scenes in SPEC:
        p=BASE/file
        require(p.is_file() and gitblob(p)==blob,"INPUT_GIT_BLOB_MISMATCH:"+key)
        m=probe(p);v=[x for x in m["streams"] if x["codec_type"]=="video"]
        require(len(v)==1 and (v[0]["width"],v[0]["height"])==(720,1280) and v[0]["codec_name"]=="h264","INPUT_FORMAT:"+key)
        require(57.8<=float(m["format"]["duration"])<=58.2,"INPUT_DURATION:"+key)
        require(not any(x["codec_type"]=="audio" for x in m["streams"]),"UNEXPECTED_SOURCE_AUDIO:"+key)
        require(scenes[0][0]==0 and scenes[-1][1]==58 and all(a[1]==b[0] for a,b in zip(scenes,scenes[1:])),"SCENE_TIMELINE")
        inputs.append((key,p,blob,source,scenes))
    tts=Vieneu(precision="int8")
    results=[]
    for key,p,blob,source,scenes in inputs:
        voice=np.zeros(TOTAL*RATE,dtype=np.float32)
        scene_proof=[]
        subtitles=[]
        for i,(start,end,line) in enumerate(scenes):
            wav=WORK/(key+f"-{i+1:02d}.wav")
            # Use official save API, then verify sample rate rather than assuming.
            tts.save(tts.infer(line,voice=VOICE,temperature=.75),str(wav))
            samples,sr=sf.read(wav,dtype="float32")
            require(sr==RATE and samples.ndim==1 and np.all(np.isfinite(samples)),"VOICE_SAMPLE_FORMAT")
            active=np.flatnonzero(np.abs(samples)>.004)
            require(len(active)>RATE*.25,"MISSING_SCENE_NARRATION")
            x=samples[max(0,active[0]-4800):min(len(samples),active[-1]+7200)]
            maxlen=round((end-start-.55)*RATE)
            original=len(x)/RATE
            ratio=max(1,len(x)/maxlen)
            require(ratio<=1.28,"NARRATION_TOO_LONG:"+key+":"+str(i+1))
            if ratio>1:
                raw=sp.check_output(["ffmpeg","-v","error","-f","f32le","-ar",str(RATE),"-ac","1","-i","pipe:0","-af",f"atempo={ratio:.6f}","-f","f32le","pipe:1"],input=np.asarray(x,dtype="<f4").tobytes())
                x=np.frombuffer(raw,dtype="<f4").copy()
            require(len(x)<=maxlen+2400,"NARRATION_SPILL")
            # Never truncate a spoken word. Fit using only short trailing silence.
            require(len(x)<=round((end-start-.25)*RATE),"NARRATION_OUTSIDE_SCENE")
            gain=min(.105/max(rms(x),1e-6),.78/max(float(np.max(np.abs(x))),1e-6))
            x=x*gain
            off=round((start+.18)*RATE)
            voice[off:off+len(x)]=x
            scene_proof.append({"scene":i+1,"start":start,"end":end,"rawVoiceSeconds":round(original,3),"voiceSeconds":round(len(x)/RATE,3),"tempo":round(ratio,3),"voiceRmsDb":round(db(rms(x)),2)})
            subtitles.append(f"{i+1}\n{stamp(start)} --> {stamp(end)}\n{line}\n")
        music=music_bed()
        active=np.abs(voice)>.008
        require(active.sum()>RATE*15,"INSUFFICIENT_NARRATION_COVERAGE")
        separation=db(rms(voice[active]))-db(rms(music[active]))
        require(separation>=18,"MUSIC_TOO_LOUD")
        mix=voice+music
        require(float(np.max(np.abs(mix)))<.95,"AUDIO_CLIP")
        wav=WORK/(key+"-mix.wav")
        sf.write(wav,np.column_stack((mix,mix)),RATE,subtype="PCM_16")
        dest=OUT/(key+"_58_GIAY_GIONG_ANH_KHOI_CHO_DUYET.mp4")
        require(not dest.exists(),"REVIEW_OUTPUT_ALREADY_EXISTS")
        original_sha=digest(p);original_packets=video_md5(p)
        run("ffmpeg","-v","error","-y","-i",p,"-i",wav,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-ar",str(RATE),"-ac","2","-t","58","-movflags","+faststart",dest)
        run("ffmpeg","-v","error","-xerror","-i",dest,"-f","null","-")
        m=probe(dest);tracks={x["codec_type"]:x for x in m["streams"]}
        require(tracks["audio"]["codec_name"]=="aac" and int(tracks["audio"]["sample_rate"])==RATE and tracks["audio"]["channels"]==2,"AUDIO_TRACK_INVALID")
        require(tracks["video"]["codec_name"]=="h264" and (tracks["video"]["width"],tracks["video"]["height"])==(720,1280),"VIDEO_TRACK_INVALID")
        require(57.8<=float(m["format"]["duration"])<=58.2,"EXPORT_DURATION")
        require(video_md5(dest)==original_packets and digest(p)==original_sha,"ORIGINAL_VISUALS_CHANGED")
        loud=sp.run(["ffmpeg","-hide_banner","-nostats","-i",str(dest),"-map","0:a:0","-af","loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json","-f","null","-"],capture_output=True,text=True,check=True)
        obj=json.loads(re.findall(r'\{\s*"input_i".*?\}',loud.stderr,re.S)[-1])
        lufs=float(obj["input_i"]);peak=float(obj["input_tp"])
        require(-24<=lufs<=-12 and peak<=-1.0,"FINAL_AUDIO_LEVEL_OUT_OF_RANGE")
        (OUT/(key+".srt")).write_text("\n".join(subtitles),encoding="utf8")
        row={"id":key,"input":p.name,"inputGitBlob":blob,"inputSha256":original_sha,"videoPacketMd5":original_packets,"videoPacketsUnchanged":True,"output":dest.name,"sha256":digest(dest),"seconds":float(m["format"]["duration"]),"resolution":"720x1280","voicePreset":VOICE,"ttsSdk":"vieneu==3.7.1","voiceLicense":"Apache-2.0; bundled preset commercial use per model card","voiceLicenseUrl":"https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo","sourceReference":source,"music":"original generated sine-note bed, no stock music","sourceMusicReused":False,"voiceOverMusicDb":round(separation,2),"integratedLufs":lufs,"truePeakDbTP":peak,"sceneProof":scene_proof,"status":"WAITING_HUMAN_LISTEN_AND_VISUAL_REVIEW","approvedForPublication":False,"approvedForBuffer":False}
        results.append(row)
        print("REAL_WINDOWS_NARRATION_PREVIEW "+json.dumps({k:v for k,v in row.items() if k!="sceneProof"},ensure_ascii=False),flush=True)
    report={"mode":"REVIEW_ONLY","videos":results,"completedAudioExports":len(results),"oldFilesModified":0,"published":0,"scheduled":0,"humanListeningVerified":False,"actualTikTokOverlayVerified":False}
    (OUT/"proof.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    readme="# Ba bản quay Windows 11 đã phối lời dẫn Anh Khôi - chờ duyệt\n\nKhông phải phê duyệt đăng. Giữ nguyên các bản quay và hàng đợi gốc. Video packets được đối chiếu MD5, lời dẫn được phối theo 5 đoạn của kịch bản đã lưu ngày 22/11. SRT là bản lời mới để rà nhịp; chữ cũ trong khung hình vẫn giữ nguyên. Cần nghe trên loa điện thoại và kiểm tra phụ đề/vùng an toàn thực tế trước khi duyệt.\n\n"
    for r in results:
        readme+=f'- [{r["id"]}]({r["output"]}) — {r["seconds"]:.2f}s, {r["integratedLufs"]:.2f} LUFS, {r["truePeakDbTP"]:.2f} dBTP; nhạc nhỏ hơn lời {r["voiceOverMusicDb"]:.1f} dB trong vùng có lời.\n'
    (OUT/"README.md").write_text(readme,encoding="utf8")
    print("BATCH01_REAL_VOICE_REVIEW_READY",len(results),flush=True)
if __name__=="__main__":main()
