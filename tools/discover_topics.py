#!/usr/bin/env python3
"""Find fresh multi-topic editorial candidates, never publish or copy articles.

Only brief title metadata, official source links, and timestamps are retained.
This collector never creates TikTok/Buffer posts, downloads news media, or
claims editorial approval.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CONFIG = Path("series/research_feeds.json")
OUT = Path("series/research_candidates.json")
LIMIT_PER_FEED = 7
TIMEOUT = 18

def plain(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

def normalize_url(s: str) -> str:
    p=urllib.parse.urlsplit(s)
    if p.scheme!="https" or not p.hostname:
        return ""
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,"",""))

def published(node: ET.Element) -> str | None:
    for name in ("pubDate", "{http://www.w3.org/2005/Atom}updated", "{http://www.w3.org/2005/Atom}published", "date"):
        v=node.findtext(name)
        if not v: continue
        try:
            parsed=email.utils.parsedate_to_datetime(v)
            if parsed.tzinfo is None: parsed=parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc).isoformat()
        except (TypeError,ValueError):
            try: return dt.datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(dt.timezone.utc).isoformat()
            except ValueError: pass
    return None

def classify_topic(headline: str, default_topic: str) -> str:
    """Mark tech exhibitions separately; never infer facts or publisher virality."""
    terms = (
        r"\\bces\\s*20[2-9][0-9]\\b", r"\\bmwc\\b",
        r"\\bcomputex\\b", r"\\bifa\\s+berlin\\b",
        "triển lãm công nghệ", "hội chợ công nghệ", "technology expo",
        "consumer electronics show", "mobile world congress",
    )
    normalized = headline.casefold()
    return "Triển lãm công nghệ" if any(re.search(t, normalized) for t in terms) else default_topic


def collect(feed: dict) -> list[dict]:
    endpoint=normalize_url(feed["url"])
    if not endpoint: raise ValueError("Invalid feed URL")
    req=urllib.request.Request(endpoint,headers={
        "User-Agent":"GocCongNgheTienIch-Editorial-Discovery/1.0 (RSS headlines and links only)",
        "Accept":"application/rss+xml,application/atom+xml,application/xml,text/xml,*/*"
    })
    with urllib.request.urlopen(req,timeout=TIMEOUT) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Non-HTTPS feed redirect")
        payload=response.read(800000)
    root=ET.fromstring(payload)
    nodes=root.findall(".//item")
    if not nodes: nodes=root.findall(".//{http://www.w3.org/2005/Atom}entry")
    now=dt.datetime.now(dt.timezone.utc)
    out=[]
    for node in nodes[:LIMIT_PER_FEED*3]:
        title=plain(node.findtext("title") or node.findtext("{http://www.w3.org/2005/Atom}title") or "")
        link=node.findtext("link") or ""
        if not link:
            a=node.find("{http://www.w3.org/2005/Atom}link")
            if a is not None: link=a.get("href","")
        link=normalize_url(link.strip())
        pub=published(node)
        if not title or not link or not pub: continue
        timestamp=dt.datetime.fromisoformat(pub)
        age=(now-timestamp).total_seconds()/3600
        if age < -3 or age > 96: continue
        out.append({
            "id":hashlib.sha256(link.encode()).hexdigest()[:16],
            "topic":classify_topic(title, feed["topic"]),
            "source_topic":feed["topic"],
            "trend_source_signal":feed.get("signal","news_research"),
            "source_tag":feed["tag"],
            "headline_reference":title[:160],
            "source_url":link,
            "published_at_utc":pub,
            "age_hours":round(max(age,0),1),
            "state":"RESEARCH_ONLY_NEEDS_FACT_CHECK_AND_RIGHTS_REVIEW"
        })
        if len(out)>=LIMIT_PER_FEED:break
    return out

def main() -> None:
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    rows=[]; failures=[]
    for feed in config["feeds"]:
        try:
            data=collect(feed)
            rows.extend(data)
            print("FEED_OK:",feed["tag"],"candidates:",len(data),flush=True)
        except (Exception) as exc:
            failures.append({"tag":feed["tag"],"error_type":type(exc).__name__})
            print("FEED_ERROR:",feed["tag"],type(exc).__name__,flush=True)
    if not rows:raise SystemExit("NO_FRESH_RSS_METADATA_CAPTURED; NO_PUBLISHING")
    seen=set();unique=[]
    for row in rows:
        if row["id"] not in seen:
            seen.add(row["id"]);unique.append(row)
    report={
        "last_collected_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "items":unique,
        "feed_failures":failures,
        "publish_permitted":False,
        "note":"Research metadata ONLY. No articles copied. No assets acquired. No videos published."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RESEARCH_CANDIDATES:",len(unique),"FAILED_FEEDS:",len(failures),"PUBLISH_PERMITTED: false")
if __name__=="__main__":
    main()
