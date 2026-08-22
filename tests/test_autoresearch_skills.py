"""Grep-based structural tests for the autoresearch skill family.

Like test_skill_structure.py, these verify the skills' load-bearing
markers exist — not prose quality.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

AR = SKILLS / "autoresearch"
STAGES = ["topics", "db", "validator", "run"]
OLD_SKILLS = [f"autoresearch-{s}" for s in STAGES]


def _skill() -> str:
    return (AR / "SKILL.md").read_text()


def _stage(name: str) -> str:
    return (AR / "references" / "stages" / f"{name}.md").read_text()


def _ref(name: str) -> str:
    return (AR / "references" / name).read_text()


# ---- autoresearch (dispatcher) ----

def test_dispatcher_has_frontmatter():
    text = _skill()
    assert text.startswith("---\nname: autoresearch\n")
    assert "description: Use when" in text


def test_dispatcher_reads_state_and_routes_to_all_stages():
    text = _skill()
    assert "research/STATE.md" in text
    for stage in STAGES:
        assert f"references/stages/{stage}.md" in text


def test_old_stage_skill_dirs_are_gone():
    for old in OLD_SKILLS:
        assert not (SKILLS / old).exists(), old
    for stage in STAGES:
        assert (AR / "references" / "stages" / f"{stage}.md").exists()


def test_dispatcher_recovers_from_missing_or_corrupt_state():
    text = _skill()
    # missing STATE.md -> initialize; corrupt -> re-derive from artifacts,
    # confirm with user before overwriting
    assert "state-schema.md" in text
    assert "re-derive" in text.lower()
    assert "confirm" in text.lower()


def test_dispatcher_verifies_gate_artifacts_before_routing():
    text = _skill()
    for artifact in ["topics.md", "research/CATALOG.md",
                     "research/INSIGHTS.md", "research/validator/manifest.json"]:
        assert artifact in text


def test_state_schema_defines_all_fields():
    text = _ref("state-schema.md")
    for field in ["stage:", "topic:", "recommended_cycle_size:", "time_limit_seconds:",
                  "authorized_attempts:", "next_attempt:", "next_cycle:",
                  "survey_gate:", "validator_gate:", "validator_env:",
                  "overrides:"]:
        assert field in text
    for stage in ["topics", "db", "validator", "run", "done"]:
        assert stage in text


# ---- stage: topics ----

def test_topics_stage_file_has_no_frontmatter():
    text = _stage("topics")
    assert not text.startswith("---")
    assert text.lstrip().startswith("# Stage")


def test_topics_scores_four_suitability_criteria():
    text = _stage("topics")
    for criterion in ["Checkable", "Cheap", "Headroom", "Publishable"]:
        assert criterion in text


def test_topics_writes_topics_md_with_metrics_placeholder():
    text = _stage("topics")
    assert "topics.md" in text
    assert "### Metrics" in text


def test_topics_derives_primary_and_guard_metrics():
    text = _stage("topics")
    assert "primary" in text
    assert "guard" in text
    assert "gaming" in text.lower()


def test_topics_lets_user_pick_and_advances_stage():
    text = _stage("topics")
    assert "AskUserQuestion" in text
    assert "stage: db" in text


# ---- stage: db ----

def test_db_stage_file_has_no_frontmatter():
    text = _stage("db")
    assert not text.startswith("---")
    assert text.lstrip().startswith("# Stage")


def test_db_delegates_paper_acquisition_to_download_ref():
    text = _stage("db")
    assert "download-ref" in text
    assert ".knowledge" in text


def test_db_checks_insight_coverage_before_distilling():
    text = _stage("db")
    assert "insight area" in text.lower()
    assert "coverage" in text.lower()


def test_db_distills_and_lets_user_select_insights():
    text = _stage("db")
    assert "research/INSIGHTS.md" in text
    assert "AskUserQuestion" in text
    assert "Shelved" in text


def test_db_builds_catalog_with_status_vocabulary():
    text = _stage("db")
    assert "research/CATALOG.md" in text
    for status in ["reproduced", "pinned", "paper-only"]:
        assert status in text


def test_db_owns_survey_gate():
    text = _stage("db")
    assert "survey_gate" in text
    assert "stage: validator" in text


def test_insights_template_defines_entry_fields():
    text = _ref("insights-template.md")
    for marker in ["## Selected", "## Shelved", "**Technique**",
                   "**Applies when**", "**Limits**", "**Sources**"]:
        assert marker in text


# ---- stage: validator ----

def test_validator_stage_file_has_no_frontmatter():
    text = _stage("validator")
    assert not text.startswith("---")
    assert text.lstrip().startswith("# Stage")


def test_validator_defines_publishable_bar_and_sealed_holdout():
    text = _stage("validator")
    assert "publishable bar" in text.lower()
    assert "research/benchmark/private/" in text
    assert "gitignore" in text.lower()


def test_validator_docker_default_with_recorded_fallback():
    text = _stage("validator")
    assert "Docker" in text
    assert "fallback" in text.lower()
    assert "manifest.json" in text


def test_validator_owns_validator_gate():
    text = _stage("validator")
    assert "validator_gate" in text
    assert "stage: run" in text


def test_contract_specifies_cli_and_json_report():
    text = _ref("validator-contract.md")
    assert "validate" in text
    for key in ['"status"', '"score"', '"per_instance"', '"errors"']:
        assert key in text
    assert "exit code" in text.lower()


def test_negative_controls_cover_four_cases():
    text = _ref("negative-controls.md")
    for control in ["cheater", "wrong-answer", "timeout", "env-escape"]:
        assert control in text


# ---- stage: run ----

def test_run_stage_file_has_no_frontmatter():
    text = _stage("run")
    assert not text.startswith("---")
    assert text.lstrip().startswith("# Stage")


def test_run_refuses_until_both_gates_passed():
    text = _stage("run")
    assert "survey_gate" in text
    assert "validator_gate" in text
    assert "refuse" in text.lower()


def test_run_enforces_hard_rules():
    text = _stage("run")
    assert ".worktrees/attempt-" in text
    assert "LOG.md" in text
    assert "time_limit_seconds" in text
    assert "holdout" in text.lower()


def test_run_draws_attempts_from_selected_insights():
    text = _stage("run")
    assert "research/INSIGHTS.md" in text
    assert "Selected" in text


def test_run_soft_gate_on_authorized_attempts():
    text = _stage("run")
    assert "authorized_attempts" in text
    assert "recommended_cycle_size" in text
    assert "ranked directions" in text
    assert "how many attempts" in text


def test_cycle_size_is_configured_up_front_but_adjustable_by_agent():
    dispatcher = _skill()
    schema = _ref("state-schema.md")
    run = _stage("run")
    assert "ask the user for a recommended number of" in dispatcher
    assert "attempts per cycle" in dispatcher
    assert "guidance, not a cap" in schema
    assert "choose the actual `cycle_size`" in " ".join(run.split())
    assert "never exceed remaining `authorized_attempts`" in run
    assert "batch_size" not in run


def test_run_confirms_first_batch_plan():
    text = _stage("run")
    assert "**Confirm the plan.**" in text


def test_run_proposals_not_limited_to_selected_insights():
    text = _stage("run")
    assert "not a fence" in text
    db = _stage("db")
    assert "not a cap" in db


def test_validator_confirms_method_with_user():
    text = _stage("validator")
    assert "validation method" in text
    assert "time_limit_seconds" in text
    assert "5 min" in text


def test_run_writes_reflection_reports():
    text = _stage("run")
    assert "docs/discussion/" in text
    assert "reflection-template.md" in text


def test_attempt_protocol_defines_log_and_scoring():
    text = _ref("attempt-protocol.md")
    assert "LOG.md" in text
    assert "validate" in text
    assert "never silently retried" in text


def test_reflection_template_has_review_lessons_next_shape():
    text = _ref("reflection-template.md")
    for section in ["## Review — what we did", "## Lessons we learnt",
                    "### Evidence carried forward", "### Literature check",
                    "## Next round"]:
        assert section in text


def test_next_round_report_ranks_evidence_grounded_directions():
    template = _ref("reflection-template.md")
    run = _stage("run")
    schema = _ref("report-schema.md")
    for marker in ["2–4", "Why promising", "First discriminating attempt",
                   "Decision signal", "Recommendation:"]:
        assert marker in template
    assert "Generate 4–6 materially distinct candidates" in template
    assert "do not stop at the first plausible continuation" in run
    assert "same **2–4 ranked directions** from the" in run
    assert "explicit top recommendation" in schema


# ---- SOTA-informed hardening (2026-07 survey) ----

def test_validator_seals_by_construction_with_holdout_budget():
    text = _stage("validator")
    assert "by construction" in text
    assert "read-only" in text
    assert "holdout query budget" in text


def test_contract_has_precheck_and_cascade():
    text = _ref("validator-contract.md")
    assert "--precheck" in text
    assert "cascade" in text.lower()
    assert "budget" in text


def test_negative_controls_patch_harness_not_prompts():
    text = _ref("negative-controls.md")
    assert "add a control reproducing the hack" in text


def test_run_plans_with_novelty_check_and_batch_composition():
    text = _stage("run")
    assert "Novelty check" in text
    for kind in ["draft", "improve", "debug"]:
        assert kind in text.lower()
    assert "sibling" in text
    assert "ancestral" in text


def test_attempt_protocol_records_kind_and_parent_lineage():
    text = _ref("attempt-protocol.md")
    assert "**kind**" in text
    assert "**parent**" in text
    assert "--precheck" in text


def test_attempt_protocol_commits_code_log_and_report_json():
    text = _ref("attempt-protocol.md")
    assert "--out" in text
    assert "report.json" in text
    assert "Commit" in text


def test_run_syncs_worktrees_and_reports_after_each_cycle():
    text = _stage("run")
    assert "**Sync.**" in text
    assert "push main" in text
    assert "never push" in " ".join(text.split()).lower()
    assert "research/benchmark/private/" in text


def test_validator_gate_requires_artifacts_on_main():
    text = _stage("validator")
    assert "committed to the main branch" in text


def test_reflection_template_reports_honest_yield():
    text = _ref("reflection-template.md")
    assert "denominators" in text
    assert "root cause" in text.lower()


# ---- registration ----

def test_claude_md_lists_merged_autoresearch_skill():
    text = (ROOT / "CLAUDE.md").read_text()
    assert "**autoresearch**" in text
    for old in OLD_SKILLS:
        assert f"**{old}**" not in text
    for stage in STAGES:
        assert stage in text


# ---- anti-triviality + stuck refresh (2026-08 consolidation) ----

def test_run_requires_mechanism_and_prior_art_per_draft():
    text = _stage("run")
    assert "**mechanism**" in text
    assert "**prior art**" in text
    assert "gap" in text


def test_run_has_triviality_filter_and_baseline_kind():
    text = _stage("run")
    assert "**Triviality check**" in text
    assert "baseline" in text
    assert "one *baseline* per batch" in " ".join(text.split())


def test_run_ranks_on_gap_closure_with_cost_as_constraint():
    text = _stage("run")
    assert "expected gap closure" in text
    assert "constraint" in text


def test_run_defines_stuck_and_refreshes_insights_via_survey():
    text = _stage("run")
    flat = " ".join(text.split())
    assert "**Stuck**" in text
    assert "two consecutive cycles" in flat
    assert "`survey`" in text
    assert "## Candidate" in text
    assert "one refresh per cycle" in flat.lower()


def test_attempt_protocol_log_has_mechanism_prior_art_and_baseline_kind():
    text = _ref("attempt-protocol.md")
    assert "**mechanism**" in text
    assert "**prior art**" in text
    assert "`baseline`" in text


def test_insights_template_has_candidate_section():
    text = _ref("insights-template.md")
    assert "## Candidate" in text


def test_helpers_moved():
    assert (AR / "helpers" / "report.py").exists()
    assert (AR / "helpers" / "test_report.py").exists()
