"""Tests for gen_campaign.py."""

import json
import tempfile
import unittest
from pathlib import Path

import gen_campaign
import report


def make_cycle(number, attempt_id, *, metric="dev score", direction="max"):
    return {
        "schema_version": 1,
        "cycle": number,
        "date_utc": f"2026-08-{number:02d}T12:00:00Z",
        "project": "fixture-project",
        "attempts_range": [attempt_id, attempt_id],
        "attempts_remaining": 3,
        "primary_metric": {"name": metric, "direction": direction},
        "guard_metrics": [],
        "bar": {"value": 0.9, "source": "GOAL.md"},
        "best_this_cycle": 0.5,
        "best_prior": None if number == 1 else 0.4,
        "holdout": {"spent": False, "result": None},
        "attempts": [{
            "id": attempt_id,
            "kind": "draft",
            "parent": None,
            "hypothesis": f"hypothesis {attempt_id}",
            "primary": 0.5,
            "guards": {},
            "status": "improved",
            "causal_note": "measurable gain",
            "log_path": f".worktrees/attempt-{attempt_id:03d}/LOG.md",
        }],
        "reflection": {
            "review": "1 of 1 improved.",
            "evidence": "The gain was repeatable.",
            "literature": "No duplicate found.",
            "next": "Direction 1: test the mechanism.",
        },
        "lessons": [{
            "observation": "score improved",
            "root_cause": "the change removed the bottleneck",
            "evidence": "all dev instances improved",
            "implication": "deepen this branch",
            "confidence": "confirmed",
        }],
        "blacklist_new": [],
        "insight_promotions": [],
    }


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        for cycle in (make_cycle(1, 11), make_cycle(2, 21)):
            (self.directory / f"cycle-{cycle['cycle']:02d}.json").write_text(
                json.dumps(cycle), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_renders_every_cycle_attempt_and_generic_metric_note(self):
        gen_campaign.main(["--dir", str(self.directory)])
        output = (self.directory / "campaign.html").read_text(encoding="utf-8")
        self.assertIn("fixture-project — full campaign", output)
        self.assertIn("attempt-011/LOG.md", output)
        self.assertIn("attempt-021/LOG.md", output)
        self.assertIn("Primary = dev score (higher is better)", output)
        self.assertNotIn("mean tc delta", output)

    def test_optional_extra_attempts_are_escaped_and_unscored(self):
        extra = [{
            "id": 99,
            "kind": "debug",
            "parent": 21,
            "hypothesis": '<script>alert("x")</script>',
            "causal_note": "outside the scored cycle",
            "log_path": '"><img src=x onerror=alert(1)>',
        }]
        extra_path = self.directory / "campaign-extra.json"
        extra_path.write_text(json.dumps(extra), encoding="utf-8")
        gen_campaign.main(["--dir", str(self.directory),
                           "--extra", str(extra_path),
                           "--records", '<script>alert("records")</script>'])
        output = (self.directory / "campaign.html").read_text(encoding="utf-8")
        self.assertIn(">099</a>", output)
        self.assertIn("unscored", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>", output)
        self.assertNotIn("<img", output)
        self.assertIn("&quot;&gt;&lt;img", output)

    def test_duplicate_extra_attempt_is_rejected(self):
        extra_path = self.directory / "campaign-extra.json"
        extra_path.write_text(json.dumps([{
            "id": 11,
            "kind": None,
            "parent": None,
            "hypothesis": "duplicate",
            "causal_note": "duplicate id",
        }]), encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            gen_campaign.main(["--dir", str(self.directory),
                               "--extra", str(extra_path)])
        self.assertEqual(cm.exception.code, 1)

    def test_index_links_to_campaign_overview(self):
        report.main(["--cycle", "2", "--dir", str(self.directory)])
        index = (self.directory / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("full campaign overview", index)
        gen_campaign.main(["--dir", str(self.directory)])
        index = (self.directory / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="campaign.html"', index)
        self.assertIn("full campaign overview", index)

    def test_invalid_sibling_cycle_blocks_incomplete_campaign(self):
        (self.directory / "cycle-03.json").write_text("{not json",
                                                       encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            gen_campaign.main(["--dir", str(self.directory)])
        self.assertEqual(cm.exception.code, 1)
        self.assertFalse((self.directory / "campaign.html").exists())


if __name__ == "__main__":
    unittest.main()
