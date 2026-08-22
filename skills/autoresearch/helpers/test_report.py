"""Tests for report.py — run with:  python3 -m unittest discover helpers"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report


def make_attempt(i, kind="draft", parent=None, primary=0.5, status="no-change",
                 guards=None, hypothesis=None, causal_note="no effect"):
    return {
        "id": i,
        "kind": kind,
        "parent": parent,
        "hypothesis": hypothesis or f"hypothesis for attempt {i}",
        "primary": primary,
        "guards": guards if guards is not None else {"runtime_s": 120},
        "status": status,
        "causal_note": causal_note,
        "log_path": f".worktrees/attempt-{i:03d}/LOG.md",
    }


def make_cycle(n, direction="max", attempts=None, best=0.5, prior=None,
               holdout_spent=False, blacklist=None):
    if attempts is None:
        attempts = [make_attempt(n * 10 + 1)]
    return {
        "schema_version": 1,
        "cycle": n,
        "date_utc": f"2026-07-{20 + n:02d}T12:00:00Z",
        "project": "fixture-project",
        "attempts_range": [attempts[0]["id"], attempts[-1]["id"]],
        "attempts_remaining": 20,
        "primary_metric": {"name": "dev score", "direction": direction},
        "guard_metrics": [{"name": "runtime_s", "direction": "min", "limit": 600}],
        "bar": {"value": 0.90 if direction == "max" else 0.10, "source": "GOAL.md"},
        "best_this_cycle": best,
        "best_prior": prior,
        "holdout": {"spent": holdout_spent,
                    "result": "dev 0.84 / holdout 0.81" if holdout_spent else None},
        "attempts": attempts,
        "reflection": {
            "review": "3 of 5 attempts **improved** the primary metric. "
                      "Attempts 15/30 used.",
            "evidence": "Approach `foo` is ruled out.\n\n- bullet one\n- bullet two",
            "literature": "Checked `.knowledge/`; claim still novel.",
            "next": "Try widening the ansatz. Abandon if two more cycles flatline.",
        },
        "lessons": [{
            "observation": f"cycle {n} best stayed at {best}",
            "root_cause": "the shared bottleneck is instance size, which "
                          "none of this batch's changes touched",
            "evidence": "per-instance results: no attempt moved the two "
                        "largest instances",
            "implication": "next batch must target the large-instance path",
            "confidence": "suspected",
        }],
        "blacklist_new": blacklist if blacklist is not None else [],
        "insight_promotions": [],
    }


def three_cycle_fixture():
    """Max-direction run: improvement, a flat cycle, failures/timeouts, holdout spent."""
    c1 = make_cycle(1, attempts=[
        make_attempt(11, primary=0.70, status="improved"),
        make_attempt(12, primary=0.60),
        make_attempt(13, primary=None, status="failed"),
    ], best=0.70, prior=None, blacklist=["greedy decoding (worse on every instance)"])
    c2 = make_cycle(2, attempts=[
        make_attempt(21, kind="improve", parent=11, primary=0.68),
        make_attempt(22, primary=None, status="timeout"),
    ], best=0.68, prior=0.70)  # no improvement this cycle
    c3 = make_cycle(3, attempts=[
        make_attempt(31, kind="improve", parent=11, primary=0.75, status="improved"),
        make_attempt(32, kind="debug", parent=21, primary=0.66),
        make_attempt(33, primary=0.55,
                     hypothesis='try <script>alert("xss")</script> & "quotes"'),
    ], best=0.75, prior=0.70, holdout_spent=True)
    c3["insight_promotions"] = ["Shelved insight X now looks relevant"]
    return [c1, c2, c3]


class ValidateTests(unittest.TestCase):
    def test_valid_fixture_passes(self):
        for c in three_cycle_fixture():
            self.assertEqual(report.validate_cycle(c), [])

    def test_each_missing_top_level_field_is_named(self):
        for field in report.REQUIRED_TOP:
            data = make_cycle(1)
            del data[field]
            errors = report.validate_cycle(data)
            self.assertTrue(any(f'"{field}"' in e for e in errors),
                            f"deleting {field} not reported: {errors}")

    def test_each_missing_attempt_field_is_named(self):
        for field in report.REQUIRED_ATTEMPT:
            data = make_cycle(1, attempts=[make_attempt(11), make_attempt(12)])
            del data["attempts"][1][field]
            errors = report.validate_cycle(data)
            self.assertTrue(any(f'"attempts[1].{field}"' in e for e in errors),
                            f"deleting attempts[1].{field} not reported: {errors}")

    def test_missing_reflection_section_is_named(self):
        data = make_cycle(1)
        del data["reflection"]["next"]
        errors = report.validate_cycle(data)
        self.assertTrue(any('"reflection.next"' in e for e in errors))

    def test_bad_enums_rejected(self):
        data = make_cycle(1)
        data["attempts"][0]["status"] = "exploded"
        self.assertTrue(report.validate_cycle(data))
        data = make_cycle(1)
        data["attempts"][0]["kind"] = "yolo"
        self.assertTrue(report.validate_cycle(data))
        data = make_cycle(1)
        data["primary_metric"]["direction"] = "sideways"
        self.assertTrue(report.validate_cycle(data))


class BestSoFarTests(unittest.TestCase):
    def test_max_direction(self):
        cycles = three_cycle_fixture()
        series = report.best_so_far(cycles, "max")
        self.assertEqual(series, [(1, 0.70), (2, 0.70), (3, 0.75)])

    def test_min_direction(self):
        cycles = [make_cycle(1, direction="min", best=0.30),
                  make_cycle(2, direction="min", best=0.40),
                  make_cycle(3, direction="min", best=0.25)]
        series = report.best_so_far(cycles, "min")
        self.assertEqual(series, [(1, 0.30), (2, 0.30), (3, 0.25)])

    def test_all_failed_cycle_carries_none(self):
        cycles = [make_cycle(1, best=None)]
        self.assertEqual(report.best_so_far(cycles, "max"), [(1, None)])


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for c in three_cycle_fixture():
            (self.dir / f"cycle-{c['cycle']:02d}.json").write_text(
                json.dumps(c), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, cycle):
        report.main(["--cycle", str(cycle), "--dir", str(self.dir)])

    def test_writes_cycle_html_and_index(self):
        self.run_main(3)
        self.assertTrue((self.dir / "cycle-03.html").exists())
        self.assertTrue((self.dir / "index.html").exists())

    def test_data_strings_are_escaped(self):
        self.run_main(3)
        html_out = (self.dir / "cycle-03.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert", html_out)
        self.assertIn("&lt;script&gt;", html_out)

    def test_current_cycle_chart_uses_each_attempts_raw_score(self):
        self.run_main(3)
        html_out = (self.dir / "cycle-03.html").read_text(encoding="utf-8")
        self.assertIn("<svg", html_out)
        self.assertIn("<polyline", html_out)
        self.assertIn("current-cycle dev score by attempt", html_out)
        for attempt, score in ((31, "0.75"), (32, "0.66"), (33, "0.55")):
            self.assertIn(f"<title>attempt {attempt}: {score}</title>", html_out)
        self.assertIn("current best 0.75", html_out)
        self.assertIn("target 0.9", html_out)
        self.assertIn('stroke-dasharray="2 3"', html_out)
        self.assertIn('stroke-dasharray="5 4"', html_out)
        self.assertNotIn("best-so-far", html_out)
        self.assertNotIn('class="kpis"', html_out)
        self.assertNotIn("attempts improved", html_out)

        index = (self.dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("best-so-far dev score by cycle", index)

    def test_optional_score_formula_replaces_remaining_attempt_headline(self):
        cycles = three_cycle_fixture()
        cycles[2]["score_formula"] = "score = **mean** candidate improvement"
        html_out = report.render_cycle(cycles[2], cycles)
        self.assertIn('class="score-formula"', html_out)
        self.assertIn("score = <strong>mean</strong> candidate improvement", html_out)
        self.assertNotIn("attempts remaining after this cycle", html_out)

        cycles[2]["score_formula"] = 42
        self.assertTrue(any('"score_formula" must be a non-empty string' in error
                            for error in report.validate_cycle(cycles[2])))

    def test_single_cycle_fallback_has_point_but_no_line(self):
        solo = tempfile.TemporaryDirectory()
        try:
            d = Path(solo.name)
            c = make_cycle(1, direction="min", best=0.30)
            (d / "cycle-01.json").write_text(json.dumps(c), encoding="utf-8")
            report.main(["--cycle", "1", "--dir", str(d)])
            html_out = (d / "cycle-01.html").read_text(encoding="utf-8")
            self.assertIn("<svg", html_out)
            self.assertNotIn("<polyline", html_out)
            self.assertIn("<title>attempt 11: 0.5</title>", html_out)
        finally:
            solo.cleanup()

    def test_index_lists_all_cycles(self):
        self.run_main(3)
        index = (self.dir / "index.html").read_text(encoding="utf-8")
        for n in (1, 2, 3):
            self.assertIn(f"cycle-{n:02d}.html", index)

    def test_index_hides_holdout_column_until_one_is_spent(self):
        cycles = three_cycle_fixture()
        never_spent = report.render_index(cycles[:2])
        self.assertNotIn("<th>holdout</th>", never_spent)
        after_spend = report.render_index(cycles)
        self.assertIn("<th>holdout</th>", after_spend)

    def test_attempt_statuses_render_without_headline_kpis(self):
        self.run_main(2)
        c2 = (self.dir / "cycle-02.html").read_text(encoding="utf-8")
        self.assertIn("timeout", c2)
        self.assertNotIn('class="kpis"', c2)

    def test_target_line_is_optional_and_spent_holdout_result_is_preserved(self):
        cycles = three_cycle_fixture()
        cycles[2]["bar"]["value"] = None
        html_out = report.render_cycle(cycles[2], cycles)
        self.assertIn("current best 0.75", html_out)
        self.assertNotIn('stroke-dasharray="5 4"', html_out)
        self.assertNotIn("target 0.9", html_out)
        self.assertIn("dev 0.84 / holdout 0.81", html_out)

    def test_all_failed_cycle_still_shows_available_target(self):
        attempts = [make_attempt(11, primary=None, status="failed"),
                    make_attempt(12, primary=None, status="failed")]
        cycle = make_cycle(1, attempts=attempts, best=None)
        html_out = report.render_cycle(cycle, [cycle])
        self.assertIn("no scored attempts yet", html_out)
        self.assertIn("target 0.9", html_out)
        self.assertIn('stroke-dasharray="5 4"', html_out)
        self.assertNotIn('stroke-dasharray="2 3"', html_out)

    def test_blacklist_and_promotions_highlighted(self):
        self.run_main(1)
        c1 = (self.dir / "cycle-01.html").read_text(encoding="utf-8")
        self.assertIn("greedy decoding", c1)
        self.run_main(3)
        c3 = (self.dir / "cycle-03.html").read_text(encoding="utf-8")
        self.assertIn("Shelved insight X", c3)

    def test_lineage_ordered_table(self):
        self.run_main(3)
        html_out = (self.dir / "cycle-03.html").read_text(encoding="utf-8")
        # every batch attempt appears exactly once as a linked id
        for aid in (31, 32, 33):
            self.assertEqual(html_out.count(f"attempt-{aid:03d}/LOG.md"), 1)
        # prior-cycle parents (011, 021) appear as grey ancestor rows
        self.assertEqual(html_out.count("ancestor from an earlier cycle"), 2)
        # descendants are indented under their ancestor
        self.assertIn("└", html_out)

    def test_lessons_validation(self):
        data = make_cycle(1)
        data["lessons"] = []
        self.assertTrue(any('"lessons"' in e
                            for e in report.validate_cycle(data)))
        data = make_cycle(1)
        del data["lessons"][0]["root_cause"]
        errors = report.validate_cycle(data)
        self.assertTrue(any('"lessons[0].root_cause"' in e for e in errors))
        data = make_cycle(1)
        data["lessons"][0]["root_cause"] = "   "  # blank is as bad as missing
        self.assertTrue(any('"lessons[0].root_cause"' in e
                            for e in report.validate_cycle(data)))
        data = make_cycle(1)
        data["lessons"][0]["confidence"] = "certain"
        self.assertTrue(any('"lessons[0].confidence"' in e
                            for e in report.validate_cycle(data)))

    def test_lessons_rendered(self):
        self.run_main(3)
        html_out = (self.dir / "cycle-03.html").read_text(encoding="utf-8")
        self.assertIn("instance size", html_out)  # root cause text
        self.assertGreater(html_out.index('class="lessons"'),
                           html_out.index("<h2>Lessons we learnt</h2>"))

    def test_review_think_next_structure(self):
        self.run_main(3)
        html_out = (self.dir / "cycle-03.html").read_text(encoding="utf-8")
        idx = [html_out.index("<h2>Review — what we did</h2>"),
               html_out.index("<h2>Lessons we learnt</h2>"),
               html_out.index("<h2>Next round</h2>")]
        self.assertEqual(idx, sorted(idx))
        for gone in ("<h2>Yield</h2>", "<h2>State</h2>", "<h2>Lineage"):
            self.assertNotIn(gone, html_out)

    def test_malformed_json_exits_nonzero_with_named_field(self):
        bad = make_cycle(4)
        del bad["attempts"][0]["status"]
        (self.dir / "cycle-04.json").write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            self.run_main(4)
        self.assertEqual(cm.exception.code, 1)

    def test_missing_json_exits_nonzero(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_main(9)
        self.assertEqual(cm.exception.code, 1)

    def test_invalid_sibling_json_is_skipped_not_fatal(self):
        (self.dir / "cycle-05.json").write_text("{not json", encoding="utf-8")
        self.run_main(3)  # must not raise
        self.assertTrue((self.dir / "cycle-03.html").exists())


class MarkdownTests(unittest.TestCase):
    def test_inline_and_blocks(self):
        out = report.md_to_html("A **bold** `code` [link](http://x.example/) line.\n\n- one\n- two")
        self.assertIn("<strong>bold</strong>", out)
        self.assertIn("<code>code</code>", out)
        self.assertIn('<a href="http://x.example/">link</a>', out)
        self.assertIn("<li>one</li>", out)

    def test_raw_html_in_markdown_is_escaped(self):
        out = report.md_to_html("evil <img src=x onerror=alert(1)>")
        self.assertNotIn("<img", out)


if __name__ == "__main__":
    unittest.main()
