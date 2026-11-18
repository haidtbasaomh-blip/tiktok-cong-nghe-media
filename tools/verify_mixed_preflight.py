#!/usr/bin/env python3
"""Fail-closed mixed-topic TikTok publication QA.

Outputs a comprehensive per-item report. This script never publishes or edits
TikTok/Buffer. Only an item with actual MP4 + cleared source licenses + source
validation + scene/audio QC + explicit approval may be marked publish_ready.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit

CONFIG=Path("series/editorial_safety_policy.json")
DRAFTS=Path("series/multi_topic_batch01.json")
RIGHTS=Path("series/rights_verified_footage.json")
APPROVALS=Path("series/approved_publications.json")
RESULT=Path("series/editorial_qa_latest.json")
MEDIA=Path("media-mixed")

def is_https(url):
    try:
        p=urlsplit(str(url))
        return p.scheme=="https" and bool(p.hostname) and not p.username and not p.password
    except ValueError:
        return False

def mp4_quality(path, min_sec=24, max_sec=35):
    if not path.exists() or path.stat().st_size < 80000:
        return ["mp4_missing_or_too_small"]
    issues=[]
    try:
        import imageio_ffmpeg
        reader=imageio_ffmpeg.read_frames(str(path))
        try:
            result=next(reader)
        finally:
            reader.close()
        width,height=map(int,result.get("size") or (0,0))
        if width<540 or height<960 or height<=width:
            issues.append("not_portrait_9_16_hd")
        duration=float(result.get("duration") or 0)
        if not min_sec<=duration<=max_sec:
            issues.append("duration_outside_24_35")
        if float(result.get("fps") or 0)<24:
            issues.append("framerate_below_24fps")
    except (OSError,ValueError,RuntimeError):
        issues.append("mp4_probe_unavailable")
    return issues

def main():
    cfg=json.loads(CONFIG.read_text(encoding="utf8"))
    drafts=json.loads(DRAFTS.read_text(encoding="utf8"))
    rights=json.loads(RIGHTS.read_text(encoding="utf8")) if RIGHTS.exists() else {"candidates":[]}
    approvals=json.loads(APPROVALS.read_text(encoding="utf8")) if APPROVALS.exists() else {"approved":[]}
    licensed={a.get("id"):a for a in rights.get("candidates",[])}
    approved={a.get("video_id"):a for a in approvals.get("approved",[])}
    ids=set();reports=[]
    for obj in drafts.get("items",[]):
        vid=obj.get("id","")
        issues=[]
        if not re.fullmatch("MX[0-9]{3}",vid):issues.append("invalid_video_id")
        if vid in ids:issues.append("duplicate_video_id")
        ids.add(vid)
        if not obj.get("hook") or not obj.get("close") or len(obj.get("facts",[]))<2:
            issues.append("incomplete_original_script")
        if not is_https(obj.get("source","")):
            issues.append("missing_fact_source")
        asset=MEDIA/(vid+".mp4")
        issues+=mp4_quality(asset)
        approval=approved.get(vid) or {}
        if approval.get("status")!="approved":
            issues.append("not_editorially_approved")
        if approval.get("visual_qa_pass") is not True:
            issues.append("visual_qa_not_approved")
        if approval.get("original_script_pass") is not True:
            issues.append("originality_not_verified")
        if approval.get("audio_rights_pass") is not True:
            issues.append("audio_rights_not_verified")
        if approval.get("factual_review_pass") is not True:
            issues.append("facts_not_reviewed")
        if approval.get("no_duplicate_pass") is not True:
            issues.append("duplicates_not_checked")
        # Video inspiration is not permission to reuse pictures or footage.
        # These human/editorial sign-offs must be explicit per finished video.
        if approval.get("no_creator_footage_or_screenshots_used_pass") is not True:
            issues.append("creator_footage_or_screenshot_reuse_not_cleared")
        if approval.get("independent_storyboard_pass") is not True:
            issues.append("independent_original_storyboard_not_verified")
        # Authentic, human-first documentary gate: real footage and genuine
        # sound matter more than cosmetic slides or simulated vlog claims.
        if approval.get("human_first_story_review_pass") is not True:
            issues.append("human_first_story_not_reviewed")
        if approval.get("natural_sound_or_narration_pass") is not True:
            issues.append("natural_audio_not_verified")
        if approval.get("truthful_visual_label_pass") is not True:
            issues.append("documentary_label_not_verified")
        claimed_format = str(approval.get("editorial_format") or "")
        if claimed_format not in ("field_vlog", "licensed_footage_documentary", "photo_essay", "hands_on_tutorial", "original_infographic"):
            issues.append("editorial_format_not_declared")
        if claimed_format in ("field_vlog","licensed_footage_documentary"):
            if int(approval.get("genuine_moving_shot_count") or 0) < 4:
                issues.append("fewer_than_four_genuine_video_shots")
            if approval.get("genuine_footage_rights_pass") is not True:
                issues.append("genuine_video_footage_rights_not_verified")
        if claimed_format == "field_vlog" and approval.get("firsthand_experience_confirmed") is not True:
            issues.append("falsely_or_unverified_firsthand_vlog")
        asset_ids=approval.get("licensed_asset_ids") or []
        if not asset_ids:
            issues.append("missing_video_asset_rights_ledger")
        for media_id in asset_ids:
            entry=licensed.get(media_id)
            if not entry or entry.get("clearance_status")!="approved":
                issues.append("uncleared_media_"+str(media_id))
            elif not is_https(entry.get("source_page","")) or not is_https(entry.get("license_url","")):
                issues.append("invalid_media_license_link")
            elif not re.fullmatch("[a-f0-9]{64}",str(entry.get("file_sha256") or "")):
                issues.append("missing_licensed_media_checksum")
        if approval.get("news_kind")=="breaking":
            sources=approval.get("independent_sources") or []
            domains={urlsplit(str(url)).hostname for url in sources if is_https(url)}
            if len(domains)<2:issues.append("breaking_requires_two_independent_sources")
            when=approval.get("last_verified_at_utc")
            try:
                parsed=datetime.fromisoformat(str(when).replace("Z","+00:00"))
                if datetime.now(timezone.utc)-parsed>timedelta(hours=24):issues.append("breaking_fact_check_stale")
            except ValueError:issues.append("breaking_requires_verification_time")
        issues=list(dict.fromkeys(issues))
        reports.append({"video_id":vid,"topic":obj.get("pillar"),"publish_ready":not issues,"blocking_reasons":issues})
    result={"checked_at_utc":datetime.now(timezone.utc).isoformat(),"channel":cfg["channel"],"checked_count":len(reports),
            "publish_ready":sum(x["publish_ready"] for x in reports),"blocked":sum(not x["publish_ready"] for x in reports),
            "items":reports,"note":"Only QA; never triggers TikTok/Buffer publication."}
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("EDITORIAL_QA_CHECKED",len(reports),"READY",result["publish_ready"],"BLOCKED",result["blocked"])
    for row in reports:
        print(row["video_id"],"READY" if row["publish_ready"] else "BLOCKED",",".join(row["blocking_reasons"]))
if __name__=="__main__":
    main()
