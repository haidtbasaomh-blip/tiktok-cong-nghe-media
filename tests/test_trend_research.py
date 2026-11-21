"""Offline QA for cross-topic fresh-news research and accurate 'trend' labels."""
import importlib.util
import unittest
from pathlib import Path

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,Path(path))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

discover=load("discover_topics", "tools/discover_topics.py")
ideas=load("daily_idea_lab", "tools/daily_idea_lab.py")

def row(title="CES 2027: robot va thiet bi AI", age=3, signal="news_research"):
    return {
        "id":"source-1",
        "topic":"Triển lãm công nghệ",
        "source_tag":"technology",
        "trend_source_signal":signal,
        "headline_reference":title,
        "source_url":"https://example.org/innovation/ces-2027",
        "age_hours":age,
        "published_at_utc":"2026-11-21T00:00:00Z",
        "state":"RESEARCH_ONLY_NEEDS_FACT_CHECK_AND_RIGHTS_REVIEW",
    }

class TrendResearchTests(unittest.TestCase):
    def test_technology_exhibition_detection(self):
        for title in ["CES 2027 new technology","Computex 2027 launch",
                      "MWC Barcelona showcases AI", "Triển lãm công nghệ quốc tế"]:
            self.assertEqual(discover.classify_topic(title,"Công nghệ thế giới"),"Triển lãm công nghệ")

    def test_regular_culture_is_not_expo(self):
        self.assertEqual(discover.classify_topic("Nghệ thuật trình diễn tại Hà Nội", "Văn hóa và nghệ thuật"),"Văn hóa và nghệ thuật")

    def test_trend_candidate_recent_but_not_verified_viral(self):
        r=row(signal="publisher_most_read_not_tiktok_trend")
        self.assertTrue(ideas.is_editorial_hot_candidate(r))
        d=ideas.create_drafts([r],["Original storyboard"])[0]
        screening=d["hot_topic_screening_not_verified_viral"]
        self.assertTrue(screening["editorial_candidate"])
        self.assertFalse(screening["verified_tiktok_or_youtube_trend"])
        self.assertFalse(d["publication_authorized"])
        self.assertEqual(d["target_video_seconds"],60)

    def test_stale_is_not_hot(self):
        self.assertFalse(ideas.is_editorial_hot_candidate(row(age=70,signal="publisher_most_read_not_tiktok_trend")))

    def test_reputable_feed_boost_but_not_viral_metrics(self):
        r=row(title="Một tin mới",signal="publisher_most_read_not_tiktok_trend")
        baseline=dict(r,trend_source_signal="news_research")
        self.assertGreater(ideas.rank(r),ideas.rank(baseline))

    def test_audio_realism_requirements(self):
        d=ideas.create_drafts([row()],["Original storytelling"])[0]
        v=d["voice_and_sound_direction"]
        self.assertIn("giọng Bắc",v["narrator"])
        self.assertTrue(v["human_audio_review_before_post"])
        self.assertIn("eSpeak",v["no_cheap_robot_voice"])
        self.assertTrue(d["asset_rights_verification_needed"])

if __name__=="__main__":
    unittest.main(verbosity=2)
