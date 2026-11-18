#!/usr/bin/env python3
"""Read-only free-toolchain media inspection for the TikTok studio.

Uses FFmpeg/ffprobe, Pillow, PySceneDetect. Auto-Editor is validated by the
workflow and used separately only with independently approved original/licensed
footage. This program does not approve or publish anything.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from io import BytesIO
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scenedetect import SceneManager, ContentDetector, open_video


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict:
    output = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(path)],
        capture_output=True, text=True, timeout=35, check=True
    )
    data = json.loads(output.stdout)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    fps_str = video.get("avg_frame_rate") or "0/1"
    parts = fps_str.split("/")
    fps = (float(parts[0]) / float(parts[1])) if len(parts) == 2 and float(parts[1]) else 0
    return {
        "width": int(video.get("width") or 0),
        "height": int(video.get("height") or 0),
        "fps": round(fps, 2),
        "duration_seconds": round(float(data.get("format", {}).get("duration") or 0), 2),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
        "has_audio": bool(audio)
    }


def detect_scenes(path: Path) -> dict:
    """Diagnostic only: scene cuts do not prove originality or camera footage."""
    try:
        with open_video(str(path)) as video:
            manager = SceneManager()
            manager.add_detector(ContentDetector(threshold=27))
            manager.detect_scenes(video=video, frame_skip=7, show_progress=False)
            scenes = manager.get_scene_list(start_in_scene=True)
            return {"detected_scenes": len(scenes),
                    "cut_times_seconds": [round(float(start.get_seconds()), 1)
                                          for start, end in scenes[1:]][:35],
                    "note": "Automated scene changes are diagnostics, not proof of unique content."}
    except Exception as exc:
        return {"detected_scenes": None, "error_type": type(exc).__name__,
                "note": "Scene detection failed; manual review required."}


def make_contact_sheet(video: Path, destination: Path, duration: float) -> bool:
    frames = []
    for fraction in (0.08, 0.34, 0.60, 0.86):
        seconds = min(max(0, duration - 0.5), duration * fraction)
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                 "-ss", f"{seconds:.2f}", "-i", str(video), "-frames:v", "1",
                 "-vf", "scale=240:426:force_original_aspect_ratio=decrease,"
                        "pad=240:426:(ow-iw)/2:(oh-ih)/2",
                 "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"],
                capture_output=True, timeout=40, check=True)
            with Image.open(BytesIO(result.stdout)) as item:
                frames.append(item.convert("RGB").copy())
        except (OSError, subprocess.SubprocessError, ValueError):
            break
    if len(frames) != 4:
        return False
    sheet = Image.new("RGB", (960, 490), (18, 24, 36))
    draw = ImageDraw.Draw(sheet)
    for i, img in enumerate(frames):
        sheet.paste(img, (i * 240, 0))
        draw.text((i * 240 + 12, 445), f"{int(duration * (0.08, .34, .60, .86)[i])}s",
                  fill=(255, 255, 255))
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, quality=86, optimize=True)
    return True


def inspect(video: Path, out: Path) -> dict:
    id_code = video.stem
    result = {"video_id": id_code, "source": str(video),
              "publication_authorized": False, "reasons_for_hold": [],
              "checks": {}, "checked_at_utc": datetime.now(timezone.utc).isoformat()}
    sidecar = video.with_suffix(".json")
    if not sidecar.is_file():
        result["reasons_for_hold"].append("missing_media_rights_sidecar")
        return result
    try:
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        result["reasons_for_hold"].append("invalid_media_rights_sidecar")
        return result
    actual_sha = sha256_file(video)
    result["checks"]["sha256_matches_sidecar"] = actual_sha == meta.get("sha256")
    if actual_sha != meta.get("sha256"):
        result["reasons_for_hold"].append("video_sha256_mismatch")
    details = probe(video)
    result["checks"]["technical"] = details
    technical_ok = (
        details["width"] >= 540 and details["height"] >= 960
        and abs(details["width"] / details["height"] - (9 / 16)) < 0.02
        and 24 <= details["duration_seconds"] <= 35
        and details["fps"] >= 24 and details["has_audio"]
    )
    if not technical_ok:
        result["reasons_for_hold"].append("technical_specification_needs_rework")

    # A matched open licence is useful evidence, not a full legal clearance.
    rights = meta.get("image_rights") or {}
    if rights and not all(rights.get(x) for x in
                          ("creator", "license", "license_url", "source_url", "sha256")):
        result["reasons_for_hold"].append("photo_license_evidence_incomplete")
    if meta.get("publication_status") != "ARCHIVED_NOT_PUBLISHED":
        result["reasons_for_hold"].append("unexpected_publication_state_requires_reconciliation")
    audio_note = str(meta.get("audio") or "").lower()
    if "sine" in audio_note or "synthesized tone" in audio_note:
        result["reasons_for_hold"].append("synthetic_tone_not_natural_vlog_sound")
    visual_note = str(meta.get("visual_edit") or "").lower()
    if "typographic" in visual_note or "photo motion" in visual_note:
        result["reasons_for_hold"].append("animated_photo_story_not_genuine_camera_vlog")
    result["checks"]["scene_detection"] = detect_scenes(video)
    result["checks"]["contact_sheet_created"] = make_contact_sheet(
        video, out / "contact-sheets" / (id_code + ".jpg"), details["duration_seconds"])
    if not result["checks"]["contact_sheet_created"]:
        result["reasons_for_hold"].append("contact_sheet_generation_failed")
    # Creative, copyright and factual approval are NEVER inferred from software tests.
    result["reasons_for_hold"].append("independent_human_editorial_rights_review_not_complete")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="media-mixed")
    parser.add_argument("--output-dir", default="reports/free-creator-tools")
    args = parser.parse_args()
    root = Path(args.input_dir)
    out = Path(args.output_dir)
    if not root.is_dir():
        raise SystemExit("INPUT_DIRECTORY_NOT_FOUND")
    clips = sorted(root.glob("MX[0-9][0-9][0-9].mp4"))
    if not clips:
        raise SystemExit("NO_ARCHIVED_MP4_FOUND")
    out.mkdir(parents=True, exist_ok=True)
    videos = [inspect(p, out) for p in clips]
    summary = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
               "video_count": len(videos), "publication_approvals": 0,
               "hold_count": sum(bool(x["reasons_for_hold"]) for x in videos),
               "toolchain": ["FFmpeg", "ffprobe", "PySceneDetect", "Pillow"],
               "auto_editor": "available separately for APPROVED licensed input only",
               "no_tiktok_or_buffer_changes": True, "videos": videos}
    (out / "audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = [
        "# TikTok Free Creator Toolchain – Báo cáo kiểm tra",
        "",
        f"- Kiểm tra: {len(videos)} video đã lưu; video được tự động duyệt đăng: **0**.",
        "- Kiểm tra tự động chỉ phát hiện tín hiệu kỹ thuật, không kết luận bản quyền hợp lệ.",
        "- Không có thao tác đăng, sửa lịch hoặc kết nối Buffer/TikTok.",
        "",
        "| Video | MP4 | Số cảnh tìm được | Vấn đề phải xử lý |",
        "|---|---|---:|---|",
    ]
    for v in videos:
        tech = v["checks"].get("technical") or {}
        scenes = (v["checks"].get("scene_detection") or {}).get("detected_scenes")
        rows.append("| " + v["video_id"] + " | "
                    + f'{tech.get("width","?")}×{tech.get("height","?")}, {tech.get("duration_seconds","?")}s'
                    + " | " + (str(scenes) if scenes is not None else "chưa xác định")
                    + " | " + ", ".join(v["reasons_for_hold"]) + " |")
        print("FREE_TOOLS_QA:", v["video_id"], "SCENES:", scenes,
              "HOLD_REASONS:", len(v["reasons_for_hold"]), flush=True)
    (out / "audit.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("FREE_TOOLS_AUDIT_OK_COUNT:", len(videos),
          "PUBLISH_APPROVED:", 0, "REPORT:", str(out / "audit.json"), flush=True)


if __name__ == "__main__":
    main()
