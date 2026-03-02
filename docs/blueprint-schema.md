# Blueprint Schema Specification

## Overview

`blueprint.json` is the canonical state file for every GMPDE project. All agents read from and write to this single file. It is the source of truth.

## Schema (v1.0.0)

```json
{
  "schema_version": "1.0.0",
  "project_id": "string",
  "project_name": "string",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",

  "current_phase": 0,
  "phase_status": {
    "0": "pending | in_progress | complete | failed",
    "1": "pending | in_progress | complete | failed",
    "2": "pending | in_progress | complete | failed",
    "3": "pending | in_progress | complete | failed",
    "4": "pending | in_progress | complete | failed",
    "freeze_gate": "locked | awaiting_approval | approved | rejected",
    "5": "pending | in_progress | complete | failed",
    "6": "pending | in_progress | complete | failed",
    "7": "pending | in_progress | complete | failed",
    "8": "pending | in_progress | complete | failed"
  },

  "problem_statement": {
    "raw_idea": "string",
    "problem": "string",
    "target_user": "string",
    "constraints": ["string"],
    "exclusions": ["string"],
    "success_metrics": ["string"],
    "scope_in": ["string"],
    "scope_out": ["string"],
    "open_questions": ["string"],
    "blockers": ["string"]
  },

  "research": {
    "feasibility": "high | medium | low",
    "recommended_approach": ["string"],
    "risks": [
      {"risk": "string", "mitigation": "string"}
    ],
    "tech_evaluation": {
      "approved": ["string"],
      "concerns": ["string"],
      "rejected": ["string"]
    }
  },

  "architecture": {
    "components": [
      {
        "name": "string",
        "responsibility": "string",
        "location": "string"
      }
    ],
    "data_flow": "string",
    "api_contracts": {},
    "data_models": {},
    "tech_stack": ["string"],
    "rejected_alternatives": [
      {"option": "string", "reason": "string"}
    ],
    "implementation_order": ["string"]
  },

  "project_plan": {
    "milestones": [
      {
        "id": "string",
        "name": "string",
        "tasks": ["string"]
      }
    ],
    "tasks": [
      {
        "id": "string",
        "description": "string",
        "files": ["string"],
        "depends_on": ["string"],
        "acceptance": "string",
        "status": "pending | in_progress | complete | failed",
        "token_budget": "low | medium | high"
      }
    ],
    "parallel_opportunities": ["string"]
  },

  "reviews": {
    "research": {"verdict": "pass | pass_with_notes | fail", "issues": ["string"]},
    "architecture": {"verdict": "pass | pass_with_notes | fail", "issues": ["string"]},
    "plan": {"verdict": "pass | pass_with_notes | fail", "issues": ["string"]}
  },

  "freeze_gate": {
    "status": "locked | approved | rejected",
    "approved_at": "ISO 8601 datetime | null",
    "user_notes": "string | null"
  },

  "decisions": [
    {
      "id": "DL-NNN",
      "title": "string",
      "phase": 0,
      "date": "ISO 8601 date",
      "agent": "string",
      "context": "string",
      "decision": "string",
      "alternatives": [
        {"option": "string", "reason_rejected": "string"}
      ],
      "consequences": ["string"],
      "reverses": "DL-NNN | null"
    }
  ],

  "pipeline_version": "1.0.0"
}
```

## Rules

1. **Single source of truth** — Agents read and update blueprint.json, not scattered markdown
2. **Schema validated** — Blueprint must conform to this schema before any phase advances
3. **Versioned** — `schema_version` tracks format, `updated_at` tracks last change
4. **Append-only decisions** — Decision entries are never modified, only appended (or reversed with new entry)
5. **Phase status drives gates** — Orchestrator checks `phase_status` and `freeze_gate.status` before advancing
