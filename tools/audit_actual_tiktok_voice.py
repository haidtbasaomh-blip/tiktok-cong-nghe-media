#!/usr/bin/env python3
"""Actual archived MP4 voice QA; no social actions, no approval flag changes.

Compare the source assets used by the 11 historical Buffer records with the
two narrated remakes. Measure the actual bytes checked out by CI, not local
copies from a previous review. Machine measurements do not replace listening.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"out/voice-audit-20261124"
OUT.mkdir(parents=True,exist_ok=True)
REVIEW={
    "WINDOWS_V_NEW": ("review/WINDOWS_V_58_GIAY_QUAY_THAT_CHO_DUYET.mp4","fd7f638b55ba52bcf09e445f591fa020e632da36"),
    "WINVER_NEW": ("review/batch-01/CN010_WINVER_58_GIAY_CHO_DUYET.mp4","086d013567c09595a9fb5d087b31c3a0c0c83781")
}
OLD={f"CN{i:03}":f"media{'-pro' if i>1 else ''}/CN{i:03}.mp4" for i in range(1,12)}
def run(*args):
    return subprocess.check_output(args,stderr=subprocess.STDOUT,text=True)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(p):
    d=json.loads(run("ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)))
    video=next(s for s in d["streams"] if s["codec_type"]=="video")
    audio=next((s for s in d["streams"] if s["codec_type"]=="audio"),None)
    subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(p),"-f","null","-"],check=True)
    return {"sha256":sha(p),"gitBlob":run("git","hash-object",str(p)).strip(),"bytes":p.stat().st_size,
        "duration":float(d["format"]["duration"]),"width":video["width"],"height":video["height"],
        "videoCodec":video["codec_name"],"audioCodec":audio["codec_name"] if audio else None,
        "audioChannels":audio.get("channels") if audio else None,
        "audioSampleRate":audio.get("sample_rate") if audio else None,"decodePass":True}
def measure(p):
    log=run("ffmpeg","-hide_banner","-nostdin","-i",str(p),"-map","0:a:0","-af","loudnorm=I=-16:TP=-1:LRA=11:print_format=json","-f","null","-")
    x=json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',log)[-1])
    sil=run("ffmpeg","-hide_banner","-nostdin","-i",str(p),"-map","0:a:0","-af","silencedetect=n=-40dB:d=0.6","-f","null","-")
    seconds=sum(float(m) for m in re.findall(r"silence_duration:\s*([0-9.]+)",sil))
    return {"integratedLUFS":float(x["input_i"]),"truePeakDBTP":float(x["input_tp"]),"loudnessRangeLU":float(x["input_lra"]),"silenceDetectedSeconds":round(seconds,2)}
def audiohash(p):
    return run("ffmpeg","-v","error","-i",str(p),"-map","0:a:0","-c:a","copy","-f","md5","-").strip()
def main():
    legacy={}
    for k,path in OLD.items():
        x=inspect(ROOT/path)
        x["sourcePath"]=path
        x["archiveHasAudioTrack"]=bool(x["audioCodec"])
        x["liveTikTokAudioIndependentlyVerified"]=False
        legacy[k]=x
    new={}
    for k,(path,expected) in REVIEW.items():
        p=ROOT/path
        x=inspect(p)
        assert x["gitBlob"]==expected,"REVIEW_VIDEO_BYTES_CHANGED"
        assert 50<=x["duration"]<=90 and x["height"]>x["width"] and x["audioCodec"]
        x.update(measure(p))
        x["sourcePath"]=path
        x["audioPacketHash"]=audiohash(p)
        x["loudnessWithinEditorialTarget"]=-20<=x["integratedLUFS"]<=-14
        x["peakWithinEditorialTarget"]=x["truePeakDBTP"]<=-1
        x["humanListeningVerified"]=False
        x["audioStemsAvailable"]=False
        # Keep the original untouched; a separate normalized preview is supplied
        # only if the measured mix does not meet the target.
        if not x["loudnessWithinEditorialTarget"] or not x["peakWithinEditorialTarget"]:
            dest=OUT/(k+"_normalized_review.mp4")
            subprocess.run(["ffmpeg","-v","error","-y","-i",str(p),"-map","0:v:0","-map","0:a:0",
                "-c:v","copy","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:a","aac","-b:a","160k","-movflags","+faststart",str(dest)],check=True)
            x["normalizedPreview"]={"path":dest.name,**inspect(dest),**measure(dest)}
            assert abs(x["normalizedPreview"]["duration"]-x["duration"])<.3
            assert x["normalizedPreview"]["truePeakDBTP"]<=-1
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(p),"-vn","-c:a","libmp3lame","-b:a","128k",str(OUT/(k+"_listen.mp3"))],check=True)
        new[k]=x
    original=ROOT/"review/WINDOWS_V_58_GIAY_BAN_XEM_TRUOC.mp4"
    new["WINDOWS_V_NEW"]["matchesLicensedPresetSourceAudioPackets"]=audiohash(original)==new["WINDOWS_V_NEW"]["audioPacketHash"]
    result={"legacySourceAudit":legacy,"newReviewAudit":new,
        "legacyWithAudioTrack":sum(x["archiveHasAudioTrack"] for x in legacy.values()),
        "legacyWithoutAudioTrack":sum(not x["archiveHasAudioTrack"] for x in legacy.values()),
        "licensedPresetDocumentation":"https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo",
        "preset":"Anh Khôi (Northern male storytelling preset)",
        "humanReviewRequired":True,"approvalFlagsChanged":False,"socialPostsCreated":0,
        "note":"Audio measurements do not prove intelligibility or voice-vs-music separation. Source assets are not a direct check of the published TikTok audio."}
    (OUT/"voice-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("TIKTOK_ACTUAL_MP4_VOICE_AUDIT "+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
