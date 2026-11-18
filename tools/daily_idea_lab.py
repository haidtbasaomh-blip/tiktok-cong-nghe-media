#!/usr/bin/env python3
"""Daily original TikTok concept lab for up to 25 distinct source-backed candidates from fresh cross-topic news metadata.

This only writes a RESEARCH artifact. It never downloads creators' footage,
claims verified TikTok/YouTube view counts, fabricates facts, edits videos,
or publishes to Buffer/TikTok.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import urlsplit

ROOT=Path("series")
CANDIDATES=ROOT/"research_candidates.json"
CREATORS=ROOT/"global_tiktok_youtube_creator_inspiration.json"
OUT=ROOT/"daily_ideas_latest.json"
REPORT=ROOT/"daily_ideas_latest.md"
MAX_PER_DAY=25
SAFE_FORMATS=[
    {"id":"question_experiment","name":"Câu hỏi – ví dụ tự dựng – kết luận",
     "opening":"Điều gì khiến chuyện này đáng chú ý?",
     "beats":["Mở đầu bằng câu hỏi mới", "Đặt bối cảnh có nguồn", "Trình bày ví dụ hoặc thí nghiệm tự dựng", "Kết bằng một điều hữu ích"]},
    {"id":"myth_vs_fact","name":"Hiểu lầm – bằng chứng – giải thích",
     "opening":"Thông tin này có đúng như chúng ta nghĩ?",
     "beats":["Nêu thắc mắc, không khẳng định tin đồn", "Tìm nguồn độc lập kiểm chứng", "Minh họa đồ họa mới", "Kết luận chỉ khi có nguồn"]},
    {"id":"picture_story","name":"Một câu chuyện – ba cảnh quay thật có phép",
     "opening":"Có chi tiết nào ít người biết trong câu chuyện này?",
     "beats":["Cảnh mở đầu đã được cấp phép", "Chuyện thật và đúng địa điểm", "Góc nhìn con người hoặc văn hóa", "Kết bằng câu hỏi liên quan"]},
    {"id":"map_context","name":"Bản đồ tự dựng – bối cảnh – tác động",
     "opening":"Sự việc này liên quan đến ai và ở đâu?",
     "beats":["Dựng bản đồ mới, không lấy clip thời sự", "Nêu thông tin đã kiểm chứng", "Giải thích bối cảnh", "Nêu điều chưa xác định rõ"]},
    {"id":"three_practical_points","name":"Ba điểm đáng nhớ – hướng dẫn rõ",
     "opening":"Ba điều hữu ích cần biết về chủ đề này",
     "beats":["Nêu nhu cầu thật", "Giải thích ngắn điều 1", "Minh họa điều 2/3 bằng hình gốc", "Kết bằng cách áp dụng"]},
]
TOPIC_PRIORITIES={
 "Công nghệ Việt Nam":2.1,"Công nghệ thế giới":2.1,
 "Khoa học và vũ trụ":1.8,"Thời sự Việt Nam":1.6,
 "Thời sự quốc tế":1.4,"Thế giới":1.4,"Du lịch và Tây Bắc":1.5,
 "Thể thao":1.3,"Xã hội và đời sống":1.2
}
SENSITIVE_TERMS=("bốc cháy","cháy","hỏa hoạn","thiệt mạng","tử vong","tai nạn",
                 "đánh bom","khủng bố","chiến tranh","nổ lớn","bạo lực","shooting",
                 "deaths","killed","earthquake victims","terror attack")
def needs_sensitive_review(row):
    title=str(row.get("headline_reference") or "").casefold()
    return any(token in title for token in SENSITIVE_TERMS)

SAFE_ASSET_CHOICES={
 "Công nghệ":"quay màn hình/mô phỏng tự tạo hoặc hình thiết bị được phép dùng",
 "Thời sự":"đồ họa bản đồ tự dựng; chỉ dùng clip minh họa có phép và ghi rõ minh họa",
 "Thế giới":"bản đồ tự dựng; tránh clip người khác",
 "Du lịch":"cảnh quay thật có giấy phép; không giả nhận đã đến địa điểm",
 "Thể thao":"sơ đồ động tác/tình huống tự dựng, không dùng clip bản quyền trận đấu",
 "Khoa học":"mô phỏng gốc; ảnh khoa học với điều kiện cấp phép xác thực",
 "Đời sống":"quay hoạt động tự làm hoặc có giấy phép của chủ sở hữu",
}
def safe_https(value):
    p=urlsplit(str(value or ""))
    return p.scheme=="https" and bool(p.hostname) and not p.username and not p.password

def rank(row):
    hours=float(row.get("age_hours") or 1000)
    topic=str(row.get("topic") or "")
    return round(max(0,4-min(hours,96)/24)+TOPIC_PRIORITIES.get(topic,1),2)

def pick_candidates(rows,limit=MAX_PER_DAY):
    unique=[];seen_urls=set();seen_topics=set()
    valid=[]
    for row in rows:
        if row.get("state")!="RESEARCH_ONLY_NEEDS_FACT_CHECK_AND_RIGHTS_REVIEW":
            continue
        if needs_sensitive_review(row):
            continue  # Can research separately, never place in routine automatic top-five.
        if not safe_https(row.get("source_url")):
            continue
        if not row.get("headline_reference") or row.get("source_url") in seen_urls:
            continue
        seen_urls.add(row["source_url"])
        valid.append(row)
    valid.sort(key=lambda r:(rank(r), r.get("published_at_utc") or ""),reverse=True)
    for candidate in valid:
        topic=candidate.get("topic")
        if topic not in seen_topics:
            unique.append(candidate)
            seen_topics.add(topic)
        if len(unique)>=limit:break
    for candidate in valid:
        if len(unique)>=limit:break
        if candidate not in unique:unique.append(candidate)
    return unique[:limit]

def visual_method(topic):
    for keyword, method in SAFE_ASSET_CHOICES.items():
        if keyword.casefold() in topic.casefold():
            return method
    return "cảnh tự quay, hoạt họa tự làm hoặc cảnh quay có giấy phép xác minh từng tệp"

def create_drafts(candidates, sample_creator_names):
    drafts=[]
    for i,row in enumerate(candidates):
        form=SAFE_FORMATS[i%len(SAFE_FORMATS)]
        title=row["headline_reference"].strip()
        draft={
           "idea_id":"DI-"+hashlib.sha256(row["source_url"].encode("utf8")).hexdigest()[:12],
           "topic":row.get("topic"),
           "source_title_for_research_only":title,
           "source_url":row["source_url"],
           "source_published_at_utc":row.get("published_at_utc"),
           "editorial_potential_score_not_view_count":rank(row),
           "style_name":form["name"],
           "style_mechanism":form["id"],
           "opening_question_draft":form["opening"],
           "storyboard_checklist":form["beats"],
           "original_visuals_plan":visual_method(str(row.get("topic") or "")),
           "two_a_b_opening_ideas":[
             "Cách A: mở bằng câu hỏi thực tế, rồi mới đưa dữ kiện được kiểm chứng",
             "Cách B: mở bằng hình hoặc sơ đồ mới, giải thích nguyên nhân sau"
           ],
           "success_metrics_to_collect_after_publication":["views_first_24h","average_watch_time","completion_rate","shares","followers_gained"],
           "view_count_currently_verified":False,
           "creator_reference_names_for_structure_only":sample_creator_names[i:i+2],
           "not_a_copy_of_source_video":True,
           "fact_check_needed":True,
           "at_least_two_independent_sources_for_breaking":True,
           "asset_rights_verification_needed":True,
           "requires_manual_editorial_approval":True,
           "publication_authorized":False,
           "status":"RESEARCH_CONCEPT_NOT_A_FINISHED_VIDEO"
        }
        drafts.append(draft)
    return drafts

def main():
    if not CANDIDATES.exists() or not CREATORS.exists():
        raise SystemExit("NEEDS_RESEARCH_INPUTS_FIRST")
    news=json.loads(CANDIDATES.read_text(encoding="utf8"))
    creators=json.loads(CREATORS.read_text(encoding="utf8"))
    selection=pick_candidates(news.get("items") or [])
    sensitive_review=[{
        "topic":row.get("topic"),
        "headline_for_manual_review":row.get("headline_reference"),
        "source_url":row.get("source_url"),
        "status":"HIGH_RISK_NEWS_REQUIRES_MANUAL_EDITORIAL_FACT_CHECK"
    } for row in (news.get("items") or []) if needs_sensitive_review(row) and safe_https(row.get("source_url"))][:10]
    if not selection:raise SystemExit("NO_VALID_FRESH_FACT_SOURCES")
    names=[item["name"] for item in creators.get("creator_examples",[]) if item.get("name")]
    if not names: names=["Original visual storytelling"]
    while len(names)<MAX_PER_DAY+2:names.extend(names)
    drafts=create_drafts(selection,names)
    output={
       "checked_at_utc":datetime.now(timezone.utc).isoformat(),
       "channel":"@goccongnghetienich",
       "ideas_today":len(drafts),
       "source_type":"fresh_RSS_headline_metadata_only",
       "real_tiktok_or_youtube_viral_view_counts_retrieved":False,
       "no_fake_viral_stats":True,
       "sensitive_news_separate_review":sensitive_review,
       "high_view_video_benchmark_not_yet_automatically_measured":True,
       "examples_of_high_performing_creators_are_format_inspiration_only":True,
       "publication_authorized":False,
       "not_a_finished_video_count":True,
       "concepts":drafts
    }
    OUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    markdown=[
      "# Nhật ký ý tưởng TikTok hằng ngày (nghiên cứu, chưa đăng)",
      "",
      f"Chốt lúc {output['checked_at_utc']}; {len(drafts)} đề tài khác nhau được chọn từ tin tham khảo.",
      "",
      "**Không ghi nhận lượt xem viral thực tế của TikTok/YouTube tại bước này**; chỉ rút cách làm từ những kênh đã chọn. Mỗi ý tưởng cần xác minh thông tin và quyền hình/nhạc trước khi dựng.",
      "",
      "| # | Chủ đề | Tin dùng để nghiên cứu | Cấu trúc video mới | Điểm tiềm năng* |",
      "|---:|---|---|---|---:|"
    ]
    for index,item in enumerate(drafts,1):
        title=item["source_title_for_research_only"].replace("|"," ")
        topic=str(item["topic"]).replace("|"," ")
        markdown.append(f"| {index} | {topic} | {title[:115]} | {item['style_name']} | {item['editorial_potential_score_not_view_count']} |")
        print("DAILY_IDEA",index,topic,item["style_mechanism"],"SOURCE",item["source_url"],flush=True)
    markdown.extend(["","*Điểm tiềm năng là điểm biên tập tính từ độ mới và sự đa dạng, **không phải lượt xem hay dự báo viral**.",
       "", "## Quy tắc sau khi sản xuất","",
       "Thử 2 cách mở đầu khi có dữ liệu phân tích hợp lệ; không đăng hai video gần giống nhau chỉ để A/B test.",
       "Chỉ chọn ý tưởng có thể tạo video riêng với hình, âm thanh hợp pháp; tin nóng cần ít nhất hai nguồn độc lập.",
       "Sau khi công khai thật mới ghi view, thời gian xem, tỉ lệ xem hết và follow bằng TikTok Analytics.",
       ""])
    REPORT.write_text("\n".join(markdown),encoding="utf8")
    print("DAILY_CREATIVE_LAB_OK:",len(drafts),"ALL_RESEARCH_ONLY_NO_POSTS",flush=True)

if __name__=="__main__":
    main()
