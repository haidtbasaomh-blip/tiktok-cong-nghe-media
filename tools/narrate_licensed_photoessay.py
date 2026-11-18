#!/usr/bin/env python3
"""Voiceover upgrade for authentic-photo TikTok sample using CC BY 4.0 Piper voice.
No publication: this remains a photo essay, NOT real-moving-camera vlog footage.
"""
from __future__ import annotations
import datetime,hashlib,json,subprocess
from pathlib import Path
from huggingface_hub import hf_hub_download
BASE=Path("media-editorial")
VIDEO=BASE/"MC001.mp4"
OUT=BASE/"MC002.mp4"
SCRIPT=("Bạn đã từng thấy ruộng bậc thang Mù Cang Chải từ trên cao chưa? "
        "Những dải ruộng uốn theo sườn núi, thay đổi sắc màu theo mùa vụ. "
        "Vẻ đẹp ấy không chỉ nằm ở phong cảnh, mà còn ở công sức lao động của người dân vùng cao. "
        "Bạn muốn khám phá địa điểm nào tiếp theo?")
MODEL="vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx"
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as src:
        for chunk in iter(lambda:src.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def probe(path):
    j=json.loads(subprocess.run(["ffprobe","-v","error","-show_format","-of","json",str(path)],capture_output=True,text=True,check=True).stdout)
    return float(j["format"]["duration"])
def main():
    original=json.loads((BASE/"MC001.json").read_text(encoding="utf8"))
    if not VIDEO.exists() or sha(VIDEO)!=original["video_sha256"]:
        raise RuntimeError("SOURCE_PHOTOESSAY_INVALID")
    model=hf_hub_download(repo_id="rhasspy/piper-voices",filename=MODEL)
    config=hf_hub_download(repo_id="rhasspy/piper-voices",filename=MODEL+".json")
    wav=BASE/"MC002-voice.wav"
    subprocess.run(["python","-m","piper","-m",model,"-f",str(wav),"--",SCRIPT],
                    check=True,timeout=240)
    length=probe(wav)
    print("PIPER_REAL_VIETNAMESE_TTS_CREATED_SECONDS",length,flush=True)
    if not 12<length<30:raise RuntimeError("VOICE_DURATION_NOT_FIT_28_SECOND_CLIP")
    subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
     "-i",str(VIDEO),"-i",str(wav),"-map","0:v:0","-map","1:a:0",
     "-c:v","copy","-c:a","aac","-b:a","128k",
     "-af","loudnorm=I=-18:TP=-2:LRA=7,apad",
     "-t","28","-movflags","+faststart",str(OUT)],check=True,timeout=140)
    meta={**original,
       "video_id":"MC002","title":"Mù Cang Chải - phiên bản thuyết minh tiếng Việt",
       "video_file":str(OUT),"video_sha256":sha(OUT),
       "natural_narration":"SYNTHETIC_VIETNAMESE_TTS_PIPER_NOT_A_HUMAN_RECORDING",
       "spoken_script":SCRIPT,"voice_seconds":length,
       "voice_model_source":"https://huggingface.co/rhasspy/piper-voices/blob/main/vi/vi_VN/vais1000/medium/MODEL_CARD",
       "voice_dataset_license":"CC BY 4.0 (VAIS-1000 corpus)",
       "voice_attribution_required":True,
       "publication_status":"ARCHIVED_NOT_PUBLISHED",
       "audio_qa_reviewed_by_human":False,
       "type":"PHOTO_ESSAY_WITH_VIETNAMESE_TTS_NOT_A_CAMERA_VLOG",
       "passes_manual_editorial_review":False,"approved_for_buffer":False,
       "generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    (BASE/"MC002.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("SPOKEN_PHOTOESSAY_RENDERED",str(OUT),OUT.stat().st_size,"VOICE_SECONDS",length,"NO_POST",flush=True)
if __name__=="__main__":
    main()
