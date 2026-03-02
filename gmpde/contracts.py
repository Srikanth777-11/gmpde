"""Contracts — agent output structure, gate rules, phase transition enforcement."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional


# ── Gate result constants ────────────────────────────────────────────────────

GATE_PASS = "pass"
GATE_PASS_WITH_NOTES = "pass_with_notes"
GATE_FAIL = "fail"
GATE_AWAITING_USER = "awaiting_user"
VALID_GATES = {GATE_PASS, GATE_PASS_WITH_NOTES, GATE_FAIL, GATE_AWAITING_USER}


# ── Allowed blueprint mutations per phase ───────────────────────────────────
# Each phase agent may ONLY mutate these top-level keys in blueprint.json.
# Engine rejects mutations outside this set.

PHASE_ALLOWED_MUTATIONS: dict[int, set[str]] = {
    0: {"problem_statement", "current_phase", "phase_status"},
    1: {"research", "current_phase", "phase_status"},
    2: {"architecture", "current_phase", "phase_status"},
    3: {"project_plan", "current_phase", "phase_status"},
    4: {"reviews", "current_phase", "phase_status"},
    5: {"project_plan", "current_phase", "phase_status"},   # updates task statuses
    6: {"reviews", "current_phase", "phase_status"},
    7: {"current_phase", "phase_status"},
    8: {"current_phase", "phase_status"},
}

# decisions and updated_at are always allowed
ALWAYS_ALLOWED = {"decisions", "updated_at", "pipeline_version"}


# ── Phase transition rules ───────────────────────────────────────────────────
# Maps phase → set of valid next phases.
# Engine blocks transitions not in this map.

VALID_TRANSITIONS: dict[int, set[int]] = {
    0: {1},          # Problem clarity → Research
    1: {2},          # Research → Design
    2: {3},          # Design → Planning
    3: {4},          # Planning → Review
    4: {5},          # Review → Development (only after freeze gate approved)
    5: {6},          # Development → Testing
    6: {7},          # Testing → Deployment
    7: {8},          # Deployment → Maintenance
    8: {8},          # Maintenance → Maintenance (continuous loop)
}

# Phases that require freeze_gate = "approved" before advancing
FREEZE_REQUIRED_BEFORE: set[int] = {5}


# ── Agent output contract ────────────────────────────────────────────────────

@dataclass
class AgentOutput:
    """
    Structured contract that every agent must produce.
    Agents embed a JSON block inside their output marked with:

        ```gmpde-output
        { ... }
        ```

    If missing, engine treats it as contract violation.
    """
    gate: str                          # pass | pass_with_notes | fail | awaiting_user
    summary: str                       # one-sentence phase summary
    issues: list[str] = field(default_factory=list)    # blocking or notable issues
    decisions: list[dict] = field(default_factory=list)  # new DL-NNN entries
    mutations: dict = field(default_factory=dict)      # blueprint fields mutated

    def validate(self) -> list[str]:
        errors = []
        if self.gate not in VALID_GATES:
            errors.append(f"Invalid gate '{self.gate}'. Must be one of {VALID_GATES}")
        if not self.summary:
            errors.append("summary is required")
        return errors


def parse_agent_output(raw: str) -> tuple[AgentOutput | None, str]:
    """
    Extract structured AgentOutput from agent's raw text output.
    Returns (AgentOutput, error_message).
    error_message is empty string on success.
    """
    pattern = r"```gmpde-output\s*(\{.*?\})\s*```"
    match = re.search(pattern, raw, re.DOTALL)
    if not match:
        return None, (
            "Agent output missing required ```gmpde-output {...} ``` block. "
            "Contract violation — gate cannot be determined from prose."
        )
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        return None, f"gmpde-output block contains invalid JSON: {e}"

    output = AgentOutput(
        gate=data.get("gate", ""),
        summary=data.get("summary", ""),
        issues=data.get("issues", []),
        decisions=data.get("decisions", []),
        mutations=data.get("mutations", {}),
    )
    errors = output.validate()
    if errors:
        return None, f"AgentOutput validation failed: {errors}"

    return output, ""


def validate_mutations(phase: int, before: dict, after: dict) -> list[str]:
    """
    Compare blueprint before/after and flag any mutations outside the
    allowed set for this phase.
    """
    allowed = PHASE_ALLOWED_MUTATIONS.get(phase, set()) | ALWAYS_ALLOWED
    errors = []
    all_keys = set(before.keys()) | set(after.keys())
    for key in all_keys:
        if before.get(key) != after.get(key) and key not in allowed:
            errors.append(
                f"Phase {phase} mutated '{key}' which is not in its allowed set: {allowed}"
            )
    return errors


def validate_decisions(before: list[dict], after: list[dict]) -> list[str]:
    """
    Enforce decision log append-only semantics:
    - Existing decisions must not be modified or removed
    - New decisions must have unique IDs
    - IDs must follow DL-NNN pattern
    """
    errors = []
    before_ids = {d.get("id"): d for d in before}
    after_ids = {d.get("id"): d for d in after}

    # Check existing decisions were not modified or removed
    for did, original in before_ids.items():
        if did not in after_ids:
            errors.append(f"Decision {did} was removed — decisions are append-only")
        elif after_ids[did] != original:
            errors.append(f"Decision {did} was modified — decisions are immutable once written")

    # Check new decisions have valid unique IDs
    seen = set(before_ids.keys())
    for d in after:
        did = d.get("id", "")
        if not re.match(r"^DL-\d{3}$", did):
            errors.append(f"Decision ID '{did}' invalid — must match DL-NNN format")
        elif did in seen and did not in before_ids:
            errors.append(f"Duplicate decision ID: {did}")
        seen.add(did)

    return errors


def validate_transition(current_phase: int, next_phase: int, freeze_gate_status: str) -> list[str]:
    """
    Validate that transitioning from current_phase to next_phase is allowed.
    """
    errors = []
    valid_next = VALID_TRANSITIONS.get(current_phase, set())
    if next_phase not in valid_next:
        errors.append(
            f"Invalid phase transition: {current_phase} → {next_phase}. "
            f"Allowed transitions from phase {current_phase}: {valid_next}"
        )
    if next_phase in FREEZE_REQUIRED_BEFORE and freeze_gate_status != "approved":
        errors.append(
            f"Phase {next_phase} requires freeze_gate = 'approved'. "
            f"Current status: '{freeze_gate_status}'. Run /approve-design first."
        )
    return errors
