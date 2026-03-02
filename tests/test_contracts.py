"""Tests for contracts — gate parsing, mutation scope, decision integrity."""
import pytest
from gmpde.contracts import (
    parse_agent_output, validate_mutations, validate_decisions, validate_transition,
    GATE_PASS, GATE_FAIL, GATE_AWAITING_USER
)


# ── parse_agent_output ────────────────────────────────────────────────────────

def test_parse_valid_output_block():
    raw = '''Some prose here.

```gmpde-output
{
  "gate": "pass",
  "summary": "Phase complete",
  "issues": [],
  "decisions": [],
  "mutations": ["problem_statement"]
}
```
'''
    output, err = parse_agent_output(raw)
    assert err == ""
    assert output.gate == GATE_PASS
    assert output.summary == "Phase complete"


def test_parse_missing_block():
    _, err = parse_agent_output("Just prose, no structured block.")
    assert "missing" in err.lower()


def test_parse_invalid_gate():
    raw = '```gmpde-output\n{"gate": "unknown", "summary": "x"}\n```'
    _, err = parse_agent_output(raw)
    assert "invalid gate" in err.lower()


def test_parse_missing_summary():
    raw = '```gmpde-output\n{"gate": "pass"}\n```'
    _, err = parse_agent_output(raw)
    assert "summary" in err.lower()


# ── validate_mutations ────────────────────────────────────────────────────────

def test_mutation_within_scope_passes():
    before = {"problem_statement": {}, "current_phase": 0}
    after  = {"problem_statement": {"problem": "defined"}, "current_phase": 0}
    errors = validate_mutations(0, before, after)
    assert errors == []


def test_mutation_outside_scope_fails():
    before = {"architecture": {}, "current_phase": 0}
    after  = {"architecture": {"changed": True}, "current_phase": 0}
    errors = validate_mutations(0, before, after)  # phase 0 cannot touch architecture
    assert len(errors) > 0


def test_decisions_always_allowed():
    before = {"decisions": []}
    after  = {"decisions": [{"id": "DL-001", "title": "x", "phase": 0, "decision": "y"}]}
    errors = validate_mutations(0, before, after)
    assert errors == []


# ── validate_decisions ────────────────────────────────────────────────────────

def test_decisions_append_is_valid():
    before = [{"id": "DL-001", "title": "t", "phase": 0, "decision": "d"}]
    after  = before + [{"id": "DL-002", "title": "t2", "phase": 1, "decision": "d2"}]
    assert validate_decisions(before, after) == []


def test_decisions_removal_is_invalid():
    before = [{"id": "DL-001", "title": "t", "phase": 0, "decision": "d"}]
    errors = validate_decisions(before, [])
    assert any("removed" in e for e in errors)


def test_decisions_modification_is_invalid():
    original = {"id": "DL-001", "title": "original", "phase": 0, "decision": "d"}
    modified = {"id": "DL-001", "title": "CHANGED", "phase": 0, "decision": "d"}
    errors = validate_decisions([original], [modified])
    assert any("modified" in e for e in errors)


def test_decisions_invalid_id_format():
    before = []
    after  = [{"id": "INVALID", "title": "t", "phase": 0, "decision": "d"}]
    errors = validate_decisions(before, after)
    assert any("DL-NNN" in e for e in errors)


# ── validate_transition ───────────────────────────────────────────────────────

def test_valid_transition():
    errors = validate_transition(0, 1, "locked")
    assert errors == []


def test_invalid_transition():
    errors = validate_transition(0, 3, "locked")
    assert len(errors) > 0


def test_freeze_gate_blocks_phase_5():
    errors = validate_transition(4, 5, "locked")
    assert any("freeze" in e.lower() or "approve" in e.lower() for e in errors)


def test_freeze_gate_approved_allows_phase_5():
    errors = validate_transition(4, 5, "approved")
    assert errors == []
