"""Run Engine — create runs, snapshot blueprint, track history."""
from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .blueprint import snapshot, validate, load, save, advance_phase
from .contracts import validate_mutations, validate_decisions, parse_agent_output, GATE_PASS, GATE_PASS_WITH_NOTES, GATE_AWAITING_USER


def _runs_dir(project_dir: Path) -> Path:
    return project_dir / "runs"


def _index_path(project_dir: Path) -> Path:
    return _runs_dir(project_dir) / "run-index.json"


def _next_run_id(project_dir: Path) -> str:
    index = _load_index(project_dir)
    n = len(index.get("runs", [])) + 1
    return f"run-{n:04d}"


def _load_index(project_dir: Path) -> dict:
    path = _index_path(project_dir)
    if not path.exists():
        blueprint = load(project_dir)
        return {
            "project_id": blueprint["project_id"],
            "project_name": blueprint["project_name"],
            "pipeline_version": blueprint["pipeline_version"],
            "runs": []
        }
    return json.loads(path.read_text())


def _save_index(project_dir: Path, index: dict) -> None:
    """Atomic write — write to temp file then replace to avoid partial corruption."""
    _runs_dir(project_dir).mkdir(parents=True, exist_ok=True)
    target = _index_path(project_dir)
    with tempfile.NamedTemporaryFile("w", dir=target.parent, delete=False, suffix=".tmp") as f:
        json.dump(index, f, indent=2)
        tmp_path = Path(f.name)
    shutil.move(str(tmp_path), str(target))


def start_run(project_dir: Path, phase: int, agent: str, trigger: str = "pipeline") -> str:
    """
    Begin a new run. Snapshots blueprint.before.json.
    Returns the run_id.
    """
    blueprint = load(project_dir)
    errors = validate(blueprint)
    if errors:
        raise ValueError(f"Blueprint validation failed before run: {errors}")

    run_id = _next_run_id(project_dir)
    run_dir = _runs_dir(project_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "agent_outputs").mkdir(exist_ok=True)

    # Snapshot before state
    snapshot(project_dir, run_dir / "blueprint.before.json")

    # Write metadata (in-progress)
    metadata = {
        "run_id": run_id,
        "project_id": blueprint["project_id"],
        "pipeline_version": blueprint["pipeline_version"],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "status": "in_progress",
        "phase_executed": phase,
        "agent": agent,
        "trigger": trigger,
        "blueprint_before": "blueprint.before.json",
        "blueprint_after": None,
        "agent_output_file": "agent_outputs/output.md",
        "gate_result": None
    }
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2))

    return run_id


def complete_run(project_dir: Path, run_id: str, gate_result: str, output: str = "") -> None:
    """
    Complete a run. Enforces:
    1. Blueprint schema validation
    2. Agent output contract parsing
    3. Mutation scope enforcement (only allowed fields changed)
    If any check fails, run is marked failed — no after snapshot is created.
    """
    run_dir = _runs_dir(project_dir) / run_id
    meta_path = run_dir / "run_metadata.json"
    metadata = json.loads(meta_path.read_text())
    phase = metadata.get("phase_executed", -1)

    # 1. Schema validation
    blueprint_after = load(project_dir)
    errors = validate(blueprint_after)
    if errors:
        fail_run(project_dir, run_id, reason=f"Schema validation failed: {errors}")
        raise ValueError(f"Blueprint schema invalid after execution: {errors}")

    # 2. Agent output contract — parse structured block if present
    strict = blueprint_after.get("config", {}).get("strict_contracts", False)
    if output:
        agent_output, contract_error = parse_agent_output(output)
        if contract_error:
            if strict:
                fail_run(project_dir, run_id, reason=f"Contract violation (strict mode): {contract_error}")
                raise ValueError(f"Contract violation: {contract_error}")
            # Soft mode — log warning only
            (run_dir / "agent_outputs" / "contract_warning.txt").write_text(contract_error)
        elif agent_output:
            gate_result = agent_output.gate

    # 3. Mutation scope + decision log integrity check
    before_path = run_dir / "blueprint.before.json"
    if before_path.exists():
        blueprint_before = json.loads(before_path.read_text())

        mutation_errors = validate_mutations(phase, blueprint_before, blueprint_after)
        if mutation_errors:
            fail_run(project_dir, run_id, reason=f"Mutation scope violation: {mutation_errors}")
            raise ValueError(f"Agent mutated fields outside allowed scope: {mutation_errors}")

        decision_errors = validate_decisions(
            blueprint_before.get("decisions", []),
            blueprint_after.get("decisions", [])
        )
        if decision_errors:
            fail_run(project_dir, run_id, reason=f"Decision log integrity violation: {decision_errors}")
            raise ValueError(f"Decision log corrupted: {decision_errors}")

    # 4. Phase transition — attempt advance if gate passes
    next_phase = phase + 1 if phase < 8 else 8
    if gate_result in (GATE_PASS, GATE_PASS_WITH_NOTES):
        transition_errors = advance_phase(blueprint_after, next_phase)
        if transition_errors:
            # Transition blocked (e.g. freeze gate not approved) — don't fail run, just record
            blueprint_after["phase_status"][str(phase)] = "complete"
            metadata["transition_blocked"] = transition_errors
        save(project_dir, blueprint_after)
    elif gate_result == GATE_AWAITING_USER:
        blueprint_after["phase_status"][str(phase)] = "complete"
        blueprint_after["freeze_gate"]["status"] = "awaiting_approval"
        save(project_dir, blueprint_after)
    # gate == fail: leave phase status as-is, no transition

    # Validation passed — safe to snapshot after state
    snapshot(project_dir, run_dir / "blueprint.after.json")

    # Save agent output
    if output:
        (run_dir / "agent_outputs" / "output.md").write_text(output)

    # Update metadata
    metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    metadata["status"] = "complete"
    metadata["blueprint_after"] = "blueprint.after.json"
    metadata["gate_result"] = gate_result
    meta_path.write_text(json.dumps(metadata, indent=2))

    # Atomic index update
    index = _load_index(project_dir)
    index["runs"].append({
        "run_id": run_id,
        "phase": metadata["phase_executed"],
        "agent": metadata["agent"],
        "status": "complete",
        "started_at": metadata["started_at"],
        "completed_at": metadata["completed_at"],
        "gate_result": gate_result
    })
    _save_index(project_dir, index)


def fail_run(project_dir: Path, run_id: str, reason: str) -> None:
    """Mark a run as failed."""
    run_dir = _runs_dir(project_dir) / run_id
    meta_path = run_dir / "run_metadata.json"
    metadata = json.loads(meta_path.read_text())
    metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    metadata["status"] = "failed"
    metadata["gate_result"] = "fail"
    meta_path.write_text(json.dumps(metadata, indent=2))

    index = _load_index(project_dir)
    index["runs"].append({
        "run_id": run_id,
        "phase": metadata["phase_executed"],
        "agent": metadata["agent"],
        "status": "failed",
        "started_at": metadata["started_at"],
        "completed_at": metadata["completed_at"],
        "gate_result": "fail",
        "failure_reason": reason
    })
    _save_index(project_dir, index)


def replay(project_dir: Path, run_id: str) -> None:
    """
    Restore blueprint to the before-state of a given run.
    This resets project state to exactly before that run executed.
    """
    run_dir = _runs_dir(project_dir) / run_id
    before = run_dir / "blueprint.before.json"
    if not before.exists():
        raise FileNotFoundError(f"No blueprint.before.json found for {run_id}")
    shutil.copy2(before, project_dir / "blueprint.json")


def history(project_dir: Path) -> list[dict]:
    """Return all runs from the index."""
    return _load_index(project_dir).get("runs", [])
