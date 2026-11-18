#!/usr/bin/env python3
"""Check archived mixed-topic MP4 readability, 720x1280, 24fps, 30sec, and render previews."""
import json,hashlib,math
from pathlib import Path
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont

ARCHIVE=Path("media-mixed")
PREVIEW=Path("media-mixed-previews")
PREVIEW.mkdir(exist_ok=True)
report=[]
for i in range(1,7):
    vid=f"MX{i:03d}"
    mp4=ARCHIVE/(vid+".mp4")
    rights=json.loads((ARCHIVE/(vid+".json")).read_text(encoding="utf-8"))
    if rights["sha256"]!=hashlib.sha256(mp4.read_bytes()).hexdigest():
        raise ValueError("SHA256 mismatch "+vid)
    generator=imageio_ffmpeg.read_frames(str(mp4),pix_fmt="rgb24")
    metadata=next(generator)
    width,height=metadata["size"]
    duration=float(metadata["duration"])
    rate=float(metadata["fps"])
    frame=next(generator)
    generator.close()
    if (width,height)!=(720,1280) or abs(duration-30)>1 or abs(rate-24)>1:
        raise RuntimeError(f"Invalid video specs {vid} {width}x{height} {duration}s {rate}fps")
    img=Image.frombytes("RGB",(width,height),frame)
    img.thumbnail((360,640))
    output=PREVIEW/(vid+".jpg")
    img.save(output,quality=87)
    report.append({"id":vid,"duration":duration,"fps":rate,"width":width,"height":height,"bytes":mp4.stat().st_size,"licence":(rights.get("image_rights") or {}).get("license","Original"),"sha256":rights["sha256"],"preview":str(output)})
    print("VIDEO_QA_OK:",vid,"DURATION:",duration,"FPS:",rate,"SIZE:",width,height,"PREVIEW:",output,flush=True)
(PREVIEW/"qa_summary.json").write_text(json.dumps({"videos":report,"publication_status":"ARCHIVED_ONLY_NOT_POSTED"},indent=2)+"\n")
print("ALL_SIX_ARCHIVED_MP4S_QA_PASSED")
