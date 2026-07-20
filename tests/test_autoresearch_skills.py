"""Grep-based structural tests for the autoresearch skill family.

Like test_skill_structure.py, these verify the skills' load-bearing
markers exist — not prose quality.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

STAGE_SKILLS = [
    "autoresearch-topics",
    "autoresearch-db",
    "autoresearch-validator",
    "autoresearch-run",
]


def _read(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text()


def _ref(skill: str, name: str) -> str:
    return (SKILLS / skill / "references" / name).read_text()


# ---- autoresearch (dispatcher) ----

def test_dispatcher_has_frontmatter():
    text = _read("autoresearch")
    assert text.startswith("---\nname: autoresearch\n")
    assert "description: Use when" in text


def test_dispatcher_reads_state_and_routes_to_all_stages():
    text = _read("autoresearch")
    assert "research/STATE.md" in text
    for stage_skill in STAGE_SKILLS:
        assert stage_skill in text


def test_dispatcher_recovers_from_missing_or_corrupt_state():
    text = _read("autoresearch")
    # missing STATE.md -> initialize; corrupt -> re-derive from artifacts,
    # confirm with user before overwriting
    assert "state-schema.md" in text
    assert "re-derive" in text.lower()
    assert "confirm" in text.lower()


def test_dispatcher_verifies_gate_artifacts_before_routing():
    text = _read("autoresearch")
    for artifact in ["topics.md", "research/CATALOG.md",
                     "research/INSIGHTS.md", "research/validator/manifest.json"]:
        assert artifact in text


def test_state_schema_defines_all_fields():
    text = _ref("autoresearch", "state-schema.md")
    for field in ["stage:", "topic:", "batch_size:", "time_limit_seconds:",
                  "authorized_rounds:", "next_attempt:", "next_cycle:",
                  "survey_gate:", "validator_gate:", "validator_env:",
                  "overrides:"]:
        assert field in text
    for stage in ["topics", "db", "validator", "run", "done"]:
        assert stage in text


# ---- autoresearch-topics ----

def test_topics_has_frontmatter():
    text = _read("autoresearch-topics")
    assert text.startswith("---\nname: autoresearch-topics\n")
    assert "description: Use when" in text


def test_topics_scores_four_suitability_criteria():
    text = _read("autoresearch-topics")
    for criterion in ["Checkable", "Cheap", "Headroom", "Publishable"]:
        assert criterion in text


def test_topics_writes_topics_md_with_metrics_placeholder():
    text = _read("autoresearch-topics")
    assert "topics.md" in text
    assert "### Metrics" in text


def test_topics_derives_primary_and_guard_metrics():
    text = _read("autoresearch-topics")
    assert "primary" in text
    assert "guard" in text
    assert "gaming" in text.lower()


def test_topics_lets_user_pick_and_advances_stage():
    text = _read("autoresearch-topics")
    assert "approval-contract.md" in text
    assert "user" in text.lower()
    assert "stage: db" in text


# ---- autoresearch-db ----

def test_db_has_frontmatter():
    text = _read("autoresearch-db")
    assert text.startswith("---\nname: autoresearch-db\n")
    assert "description: Use when" in text


def test_db_delegates_paper_acquisition_to_download_ref():
    text = _read("autoresearch-db")
    assert "download-ref" in text
    assert ".knowledge" in text


def test_preapproved_db_batch_does_not_reprompt_for_each_cite_key():
    db = _read("autoresearch-db")
    download = _read("download-ref").lower()
    for marker in [
        "exact reference manifest",
        "deterministic cite-key policy",
        "single approval decision",
    ]:
        assert marker in db
    for marker in [
        "pre-authorized direct batch",
        "without per-reference prompting",
        "cite-key collision",
        "record the final mapping",
    ]:
        assert marker in download


def test_db_checks_insight_coverage_before_distilling():
    text = _read("autoresearch-db")
    assert "insight area" in text.lower()
    assert "coverage" in text.lower()


def test_db_distills_and_lets_user_select_insights():
    text = _read("autoresearch-db")
    assert "research/INSIGHTS.md" in text
    assert "approval-contract.md" in text
    assert "user" in text.lower()
    assert "Shelved" in text


def test_db_builds_catalog_with_status_vocabulary():
    text = _read("autoresearch-db")
    assert "research/CATALOG.md" in text
    for status in ["reproduced", "pinned", "paper-only"]:
        assert status in text


def test_db_owns_survey_gate():
    text = _read("autoresearch-db")
    assert "survey_gate" in text
    assert "stage: validator" in text


def test_insights_template_defines_entry_fields():
    text = _ref("autoresearch-db", "insights-template.md")
    for marker in ["## Selected", "## Shelved", "**Technique**",
                   "**Applies when**", "**Limits**", "**Sources**"]:
        assert marker in text


# ---- autoresearch-validator ----

def test_validator_has_frontmatter():
    text = _read("autoresearch-validator")
    assert text.startswith("---\nname: autoresearch-validator\n")
    assert "description: Use when" in text


def test_validator_defines_publishable_bar_and_sealed_holdout():
    text = _read("autoresearch-validator")
    assert "publishable bar" in text.lower()
    assert "research/benchmark/private/" in text
    assert "gitignore" in text.lower()


def test_validator_docker_default_with_recorded_fallback():
    text = _read("autoresearch-validator")
    assert "Docker" in text
    assert "fallback" in text.lower()
    assert "manifest.json" in text


def test_validator_owns_validator_gate():
    text = _read("autoresearch-validator")
    assert "validator_gate" in text
    assert "stage: run" in text


def test_contract_specifies_cli_and_json_report():
    text = _ref("autoresearch-validator", "validator-contract.md")
    assert "validate" in text
    for key in ['"status"', '"score"', '"per_instance"', '"errors"']:
        assert key in text
    assert "exit code" in text.lower()


def test_negative_controls_cover_four_cases():
    text = _ref("autoresearch-validator", "negative-controls.md")
    for control in ["cheater", "wrong-answer", "timeout", "env-escape"]:
        assert control in text


# ---- autoresearch-run ----

def test_run_has_frontmatter():
    text = _read("autoresearch-run")
    assert text.startswith("---\nname: autoresearch-run\n")
    assert "description: Use when" in text


def test_run_refuses_until_both_gates_passed():
    text = _read("autoresearch-run")
    assert "survey_gate" in text
    assert "validator_gate" in text
    assert "refuse" in text.lower()


def test_run_enforces_hard_rules():
    text = _read("autoresearch-run")
    assert ".worktrees/attempt-" in text
    assert "LOG.md" in text
    assert "time_limit_seconds" in text
    assert "holdout" in text.lower()


def test_run_draws_attempts_from_selected_insights():
    text = _read("autoresearch-run")
    assert "research/INSIGHTS.md" in text
    assert "Selected" in text


def test_run_soft_gate_on_authorized_rounds():
    text = _read("autoresearch-run")
    assert "authorized_rounds" in text
    assert "batch_size" in text


def test_run_writes_reflection_reports():
    text = _read("autoresearch-run")
    assert "docs/discussion/" in text
    assert "reflection-template.md" in text


def test_attempt_protocol_defines_log_and_scoring():
    text = _ref("autoresearch-run", "attempt-protocol.md")
    assert "LOG.md" in text
    assert "validate" in text
    assert "never silently retried" in text


def test_reflection_template_has_code_distance_shape():
    text = _ref("autoresearch-run", "reflection-template.md")
    for section in ["Evidence carried forward", "Literature check",
                    "Decision"]:
        assert section in text


# ---- SOTA-informed hardening (2026-07 survey) ----

def test_validator_seals_by_construction_with_holdout_budget():
    text = _read("autoresearch-validator")
    assert "by construction" in text
    assert "read-only" in text
    assert "holdout query budget" in text


def test_contract_has_precheck_and_cascade():
    text = _ref("autoresearch-validator", "validator-contract.md")
    assert "--precheck" in text
    assert "cascade" in text.lower()
    assert "budget" in text


def test_negative_controls_patch_harness_not_prompts():
    text = _ref("autoresearch-validator", "negative-controls.md")
    assert "add a control reproducing the hack" in text


def test_run_plans_with_novelty_check_and_batch_composition():
    text = _read("autoresearch-run")
    assert "Novelty check" in text
    for kind in ["draft", "improve", "debug"]:
        assert kind in text.lower()
    assert "sibling" in text
    assert "ancestral" in text


def test_attempt_protocol_records_kind_and_parent_lineage():
    text = _ref("autoresearch-run", "attempt-protocol.md")
    assert "**kind**" in text
    assert "**parent**" in text
    assert "--precheck" in text


def test_reflection_template_reports_yield():
    text = _ref("autoresearch-run", "reflection-template.md")
    assert "## Yield" in text
    assert "denominators" in text


# ---- registration ----

def test_claude_md_lists_all_autoresearch_skills():
    text = (ROOT / "CLAUDE.md").read_text()
    assert "**autoresearch**" in text
    for stage_skill in STAGE_SKILLS:
        assert stage_skill in text


# ---- portability and auditable stage approvals ----

def test_codex_install_links_real_skill_directories():
    text = (ROOT / ".codex" / "INSTALL.md").read_text()
    assert "skills/sci-brain" not in text
    assert 'for skill in "$HOME/.codex/sci-brain/skills"/*' in text
    assert 'ln -sfn "$skill"' in text


def test_approval_contract_is_portable_and_auditable():
    contract = _ref("autoresearch", "approval-contract.md")
    assert "research/APPROVALS.md" in contract
    assert "current conversation" in contract
    assert "platform" in contract.lower()
    assert "pre-authorized" in contract
    assert "never infer" in contract.lower()
    assert "do not duplicate" in contract.lower()


def test_interactive_stages_use_shared_approval_contract():
    for skill in [
        "autoresearch",
        "autoresearch-topics",
        "autoresearch-db",
        "autoresearch-validator",
    ]:
        text = _read(skill)
        assert "approval-contract.md" in text
    state = _ref("autoresearch", "state-schema.md")
    assert "approval_log:" in state


# ---- enforceable validator privacy ----

def test_validator_private_layout_is_outside_attempts():
    text = _read("autoresearch-validator")
    for marker in [
        "research/validator/private/",
        "research/benchmark/private/",
        "outside the attempt worktree",
        "fail closed",
        "policy hash",
    ]:
        assert marker in text


def test_env_escape_control_probes_both_private_roots():
    text = _ref("autoresearch-validator", "negative-controls.md")
    assert "validator/private" in text
    assert "benchmark/private" in text
    assert "network" in text


def test_contract_records_private_hashes_without_labels():
    text = _ref("autoresearch-validator", "validator-contract.md")
    assert "scorer_hash" in text
    assert "holdout_hash" in text
    assert "sandbox_policy_hash" in text
    assert "never labels" in text.lower()


# ---- reproducible attempt worktrees ----

def test_state_records_committed_attempt_baseline():
    text = _ref("autoresearch", "state-schema.md")
    assert "baseline_commit:" in text


def test_run_preflights_worktree_and_clean_baseline():
    text = _read("autoresearch-run")
    for marker in [
        "git check-ignore -q --no-index .worktrees/",
        "git status --porcelain",
        "git merge-base --is-ancestor",
        "baseline_commit",
        "public pipeline artifacts",
        "refuse",
    ]:
        assert marker in text


def test_attempt_creation_names_branch_and_parent_ref():
    text = _ref("autoresearch-run", "attempt-protocol.md")
    assert "git worktree add -b autoresearch/attempt-NNN" in text
    assert "<parent-ref>" in text
    assert "**base commit**" in text
    assert "**result commit**" in text
