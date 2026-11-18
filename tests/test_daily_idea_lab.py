"""No-video, no-view-fabrication regression tests for the daily idea lab."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("daily_idea_lab",Path("tools/daily_idea_lab.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def row(topic, key, age=8):
    return {
      "topic":topic,"id":key,"headline_reference":"A research headline for topic "+topic,
      "source_url":"https://example.org/articles/"+key,
      "age_hours":age, "published_at_utc":"2026-11-18T12:00:00Z",
      "state":"RESEARCH_ONLY_NEEDS_FACT_CHECK_AND_RIGHTS_REVIEW",
    }

class DailyIdeaLabTests(unittest.TestCase):
    def test_diverse_topics_over_repeat(self):
        rows=[row("Công nghệ Việt Nam","1",1),row("Công nghệ Việt Nam","2",2),
              row("Thể thao","3",5),row("Khoa học và vũ trụ","4",4)]
        selected=m.pick_candidates(rows,3)
        self.assertEqual(len(selected),3)
        self.assertEqual(len({x["topic"] for x in selected}),3)
    def test_bad_urls_rejected(self):
        rows=[row("Thể thao","1")]
        rows[0]["source_url"]="http://example.org/not-secure"
        self.assertEqual(m.pick_candidates(rows),[])
    def test_never_publish_or_fake_views(self):
        drafts=m.create_drafts([row("Du lịch và Tây Bắc","1")],["SampleCreator","ExampleCreator"])
        self.assertEqual(len(drafts),1)
        d=drafts[0]
        self.assertFalse(d["publication_authorized"])
        self.assertFalse(d["view_count_currently_verified"])
        self.assertTrue(d["fact_check_needed"])
        self.assertTrue(d["asset_rights_verification_needed"])
        self.assertTrue(d["not_a_copy_of_source_video"])
    def test_duplicate_research_source_only_once(self):
        self.assertEqual(len(m.pick_candidates([row("Thể thao","1"),row("Thể thao","1")],5)),1)

if __name__=="__main__":
    unittest.main(verbosity=2)
