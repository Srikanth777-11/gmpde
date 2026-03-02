"""Tests for blueprint load/save/validate/advance_phase."""
import json
import pytest
from pathlib import Path
from gmpde.blueprint import init, load, save, validate, advance_phase


@pytest.fixture
def project(tmp_path):
    return init(tmp_path, "test-proj", "Test Project", "Build something cool")


def test_init_creates_blueprint(project, tmp_path):
    bp = load(tmp_path)
    assert bp["project_id"] == "test-proj"
    assert bp["current_phase"] == 0
    assert bp["freeze_gate"]["status"] == "locked"


def test_validate_passes_fresh_blueprint(project, tmp_path):
    bp = load(tmp_path)
    errors = validate(bp)
    assert errors == []


def test_validate_fails_missing_field(tmp_path):
    (tmp_path / "blueprint.json").write_text(json.dumps({"project_id": "x"}))
    bp = load(tmp_path)
    errors = validate(bp)
    assert any("project_name" in e for e in errors)


def test_advance_phase_valid(project, tmp_path):
    bp = load(tmp_path)
    errors = advance_phase(bp, 1)
    assert errors == []
    assert bp["current_phase"] == 1


def test_advance_phase_invalid_transition(project, tmp_path):
    bp = load(tmp_path)
    errors = advance_phase(bp, 5)  # can't jump from 0 to 5
    assert len(errors) > 0


def test_advance_phase_blocked_by_freeze_gate(project, tmp_path):
    bp = load(tmp_path)
    bp["current_phase"] = 4
    save(tmp_path, bp)
    bp = load(tmp_path)
    errors = advance_phase(bp, 5)  # requires freeze_gate = approved
    assert any("freeze_gate" in e or "approve" in e.lower() for e in errors)
