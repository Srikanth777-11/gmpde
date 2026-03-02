# Hierarchical Agent Pipeline — Project Rules

## Overview
This project uses a hierarchical multi-agent pipeline to go from idea to deployed software. The pipeline is controlled by the `orchestrator` agent, which coordinates specialized agents across 8 phases.

## Agent Hierarchy

```
orchestrator (Opus, red) — Master controller, phase management
├── Phase 0: Problem Clarity
│   └── problem-clarifier (Sonnet, white) — Problem definition & scope
├── Phase 1: Research
│   ├── idea-researcher (Sonnet, blue) — Feasibility & discovery
│   └── tech-scout (Haiku, blue) — Technology evaluation
├── Phase 2: Design
│   └── architect (Opus, yellow) — System design & ADR
├── Phase 3: Planning
│   └── project-planner (Sonnet, green) — Task decomposition
├── Phase 4: Review
│   └── doc-reviewer (Sonnet, orange) — Quality gates
│
│   🔒 USER FREEZE GATE — /approve-design required before implementation
│
├── Phase 5: Development
│   ├── implementer (Sonnet, cyan) — Code writing
│   └── code-optimizer (Sonnet, cyan) — Post-implementation polish
├── Phase 6: Testing
│   ├── test-writer (Sonnet, magenta) — Test development
│   └── qa-validator (Sonnet, magenta) — Final QA
├── Phase 7: Deployment
│   └── deployer (Sonnet, red) — Build & deploy
└── Phase 8: Maintenance
    └── monitor (Haiku, green) — Health & monitoring
```

## Token Conservation Protocol (ALL AGENTS MUST FOLLOW)

### Rule 1: Compressed Context
Never pass full file contents between agents. Use:
- File paths with line ranges: `src/auth/AuthService.java:45-120`
- Summaries: "AuthService handles JWT token generation and validation"
- Decision references: "Per ADR section 'API Contracts'"

### Rule 2: Scoped Reading
- Research agents: max 10 files
- Design agents: max 8 files
- Implementation agents: max 5 files per task
- Test agents: max 4 files per task
- Review agents: max files in artifact + 3 spot-checks

### Rule 3: Output Limits
| Agent | Max Output |
|-------|-----------|
| problem-clarifier | 400 words |
| idea-researcher | 500 words |
| tech-scout | 300 words |
| architect | 800 words |
| project-planner | 600 words |
| doc-reviewer | 400 words |
| implementer | Task report only |
| code-optimizer | 200 words |
| test-writer | Test code + 300 word report |
| qa-validator | 400 words |
| deployer | 300 words |
| monitor | 200 words |

### Rule 4: Early Termination
If an agent finds its answer in the first 2 files it reads, it stops reading more files.

### Rule 5: No Scope Creep
Each agent does ONLY its designated role. If an agent discovers work outside its scope, it reports it and stops — it does NOT do the work.

## Document Conventions

All artifacts go in the `docs/` directory:
```
docs/
├── problem-statement.md    (Phase 0 output)
├── decision-log.md         (ALL phases append here)
├── research-brief.md       (Phase 1 output)
├── adr.md                  (Phase 2 output)
├── project-plan.md         (Phase 3 output)
├── reviews/                (Phase 4 outputs)
│   ├── research-review.md
│   ├── adr-review.md
│   └── plan-review.md
├── design-approval.md      (Freeze gate — user approval record)
├── task-reports/            (Phase 5 outputs)
│   ├── T-001.md
│   └── T-002.md
├── test-reports/            (Phase 6 outputs)
│   ├── T-001-tests.md
│   └── T-002-tests.md
├── qa-report.md            (Phase 6 final output)
└── deploy-report.md        (Phase 7 output)
```

## Communication Protocol

Agents communicate through:
1. **Document artifacts** — Written to `docs/` following the structure above
2. **Task dispatches from orchestrator** — Using the standard format:
   ```
   PHASE: [phase_name]
   TASK_ID: [unique_id]
   SCOPE: [specific files/modules]
   INPUT: [compressed context]
   EXPECTED_OUTPUT: [specific deliverable]
   TOKEN_BUDGET: [low/medium/high]
   ```
3. **Quality gate verdicts** — ✅ PASS / ⚠️ PASS WITH NOTES / 🚫 FAIL

Agents NEVER communicate directly with each other. All coordination goes through the orchestrator.

## Phase Gate Rules

1. No phase advances without its predecessor producing the required artifact
2. The doc-reviewer must approve Phase 0-3 artifacts before advancement
3. **🔒 FREEZE GATE: After Phase 4, the pipeline STOPS. No implementation begins until the user runs `/approve-design`. The orchestrator must present a design summary and wait for explicit user approval. This is non-negotiable.**
4. The qa-validator must approve Phase 5-6 outputs before deployment
5. If a gate fails, the orchestrator routes back to the MINIMUM scope needed to fix
6. Maximum 2 retry loops per phase — after that, escalate to the user

## Decision Log Rules

Every agent that makes a significant decision must append an entry to `docs/decision-log.md`:
- **What** was decided
- **Why** (context and rationale)
- **What alternatives** were considered and rejected
- **What consequences** follow from this decision

This is the project's institutional memory. Without it, context is lost.

## Model Assignment Strategy

- **Opus**: orchestrator, architect — Complex reasoning, system-level decisions
- **Sonnet**: problem-clarifier, idea-researcher, implementer, test-writer, project-planner, doc-reviewer, qa-validator, deployer, code-optimizer — Focused execution tasks
- **Haiku**: tech-scout, monitor — Quick evaluations, lightweight checks

This minimizes cost while keeping quality where it matters most.
