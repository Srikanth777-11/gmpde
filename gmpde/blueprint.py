"""Blueprint — load, validate, save canonical project state."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "blueprint.schema.json"
TEMPLATE_PATH = Path(__file__).parent.parent / "schema" / "blueprint.template.json"


def load(project_dir: Path) -> dict:
    """Load blueprint.json from project directory."""
    path = project_dir / "blueprint.json"
    if not path.exists():
        raise FileNotFoundError(f"No blueprint.json found in {project_dir}")
    return json.loads(path.read_text())


def save(project_dir: Path, blueprint: dict) -> None:
    """Save blueprint.json, updating updated_at timestamp."""
    blueprint["updated_at"] = datetime.now(timezone.utc).isoformat()
    path = project_dir / "blueprint.json"
    path.write_text(json.dumps(blueprint, indent=2))


def init(project_dir: Path, project_id: str, project_name: str, raw_idea: str) -> dict:
    """Create a new blueprint.json from template."""
    template = json.loads(TEMPLATE_PATH.read_text())
    now = datetime.now(timezone.utc).isoformat()
    template["project_id"] = project_id
    template["project_name"] = project_name
    template["created_at"] = now
    template["updated_at"] = now
    template["problem_statement"]["raw_idea"] = raw_idea
    project_dir.mkdir(parents=True, exist_ok=True)
    save(project_dir, template)
    return template


def snapshot(project_dir: Path, dest: Path) -> None:
    """Copy current blueprint.json to dest path (for run snapshots)."""
    shutil.copy2(project_dir / "blueprint.json", dest)


def advance_phase(blueprint: dict, next_phase: int) -> list[str]:
    """
    Validate and apply a phase transition.
    Returns list of errors; empty means transition is allowed.
    Imports contracts lazily to avoid circular import.
    """
    from .contracts import validate_transition
    current = blueprint.get("current_phase", 0)
    freeze_status = blueprint.get("freeze_gate", {}).get("status", "locked")
    errors = validate_transition(current, next_phase, freeze_status)
    if not errors:
        blueprint["current_phase"] = next_phase
        blueprint["phase_status"][str(next_phase)] = "in_progress"
    return errors


def validate(blueprint: dict) -> list[str]:
    """
    Basic structural validation. Returns list of error strings.
    Returns empty list if valid.
    """
    errors = []
    required = ["schema_version", "project_id", "project_name", "current_phase",
                "phase_status", "problem_statement", "decisions", "pipeline_version"]
    for field in required:
        if field not in blueprint:
            errors.append(f"Missing required field: {field}")

    if "freeze_gate" in blueprint:
        valid_status = {"locked", "awaiting_approval", "approved", "rejected"}
        if blueprint["freeze_gate"].get("status") not in valid_status:
            errors.append("freeze_gate.status must be one of: locked, awaiting_approval, approved, rejected")

    if "decisions" in blueprint:
        ids_seen = set()
        for d in blueprint["decisions"]:
            did = d.get("id", "")
            if did in ids_seen:
                errors.append(f"Duplicate decision ID: {did}")
            ids_seen.add(did)

    return errors
