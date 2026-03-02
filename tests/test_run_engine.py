"""Tests for run engine lifecycle."""
import pytest
from pathlib import Path
from gmpde.blueprint import init, load
from gmpde.run_engine import start_run, complete_run, fail_run, replay, history


@pytest.fixture
def project(tmp_path):
    init(tmp_path, "run-test", "Run Test", "Test the run engine")
    return tmp_path


def test_start_run_creates_directory(project):
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    run_dir = project / "runs" / run_id
    assert run_dir.exists()
    assert (run_dir / "blueprint.before.json").exists()
    assert (run_dir / "run_metadata.json").exists()


def test_run_id_is_four_digit(project):
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    assert run_id == "run-0001"


def test_complete_run_creates_after_snapshot(project):
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    complete_run(project, run_id, gate_result="pass", output="[SIMULATED] done.")
    assert (project / "runs" / run_id / "blueprint.after.json").exists()


def test_complete_run_advances_phase(project):
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    complete_run(project, run_id, gate_result="pass")
    bp = load(project)
    assert bp["current_phase"] == 1


def test_complete_run_fail_does_not_advance(project):
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    complete_run(project, run_id, gate_result="fail")
    bp = load(project)
    assert bp["current_phase"] == 0


def test_fail_run_marks_status(project):
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    fail_run(project, run_id, reason="test failure")
    runs = history(project)
    assert runs[-1]["status"] == "failed"


def test_replay_restores_blueprint(project):
    original_phase = load(project)["current_phase"]
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    complete_run(project, run_id, gate_result="pass")
    assert load(project)["current_phase"] == 1

    replay(project, run_id)
    assert load(project)["current_phase"] == original_phase


def test_history_grows_with_runs(project):
    start_run(project, phase=0, agent="problem-clarifier")
    assert len(history(project)) == 0  # not complete yet
    run_id = start_run(project, phase=0, agent="problem-clarifier")
    complete_run(project, run_id, gate_result="pass")
    assert len(history(project)) == 1
