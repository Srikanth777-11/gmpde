# GMPDE — Governed Multi-Agent Project Development Engine

[![CI](https://github.com/yourusername/gmpde/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/gmpde/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A framework that uses AI agents to design, plan, review, and build software projects through strict governance phases. Every idea goes through structured clarification, architecture, planning, and review before a single line of code is written.

## What It Does

Instead of jumping straight to code, GMPDE enforces a disciplined pipeline:

```
Phase 0: Problem Clarity    → Clarify what you're actually building
Phase 1: Research            → Feasibility analysis and tech evaluation
Phase 2: Design              → Architecture Decision Record (ADR)
Phase 3: Planning            → Task decomposition with dependencies
Phase 4: Review              → Quality gates on all artifacts
         FREEZE GATE         → You approve before any code is written
Phase 5: Development         → Agents implement task by task
Phase 6: Testing             → Automated test writing + QA validation
Phase 7: Deployment          → Build, deploy, verify
Phase 8: Maintenance         → Health monitoring
```

Every decision is logged. Every phase has a gate. Nothing advances without approval.

## Installation

### Prerequisites
- [Claude Code CLI](https://claude.ai/claude-code) installed and authenticated

### Install into your project
```bash
git clone https://github.com/yourusername/gmpde.git
cd gmpde
bash install.sh
```

The installer copies agents and commands into your `.claude/` directory.

## Usage

### Start a full pipeline
```
/pipeline Build a real-time notification system
```

The orchestrator will:
1. Run Phase 0 to clarify your idea
2. Progress through research, design, planning, review
3. Stop at the freeze gate for your approval
4. Only then begin implementation

### Approve design to unlock implementation
```
/approve-design
```

### Run a single agent directly
```
/quick-task architect Review the current API design
```

## Agent Hierarchy

| Agent | Model | Role |
|-------|-------|------|
| orchestrator | Opus | Master controller, phase management |
| problem-clarifier | Sonnet | Phase 0 — problem definition and scope |
| idea-researcher | Sonnet | Phase 1 — feasibility and discovery |
| tech-scout | Haiku | Phase 1 — technology evaluation |
| architect | Opus | Phase 2 — system design and ADR |
| project-planner | Sonnet | Phase 3 — task decomposition |
| doc-reviewer | Sonnet | Phase 4 — quality gate reviews |
| implementer | Sonnet | Phase 5 — code writing |
| code-optimizer | Sonnet | Phase 5 — post-implementation polish |
| test-writer | Sonnet | Phase 6 — test development |
| qa-validator | Sonnet | Phase 6 — final QA |
| deployer | Sonnet | Phase 7 — build and deploy |
| monitor | Haiku | Phase 8 — health monitoring |

## Governance Features

- **Phase Gates** — No phase advances without its predecessor producing the required artifact
- **Freeze Gate** — Human approval required before any implementation begins
- **Decision Log** — Every significant decision tracked with context, alternatives, and consequences
- **Token Conservation** — Strict output limits and scoped file reading per agent
- **No Scope Creep** — Agents do only their designated role; out-of-scope work is reported, not done

## Project Output Structure

Each pipeline run produces:
```
docs/
├── problem-statement.md      # Phase 0
├── decision-log.md           # All phases
├── research-brief.md         # Phase 1
├── tech-evaluation.md        # Phase 1
├── adr.md                    # Phase 2
├── project-plan.md           # Phase 3
├── reviews/                  # Phase 4
├── design-approval.md        # Freeze gate
├── task-reports/             # Phase 5
├── test-reports/             # Phase 6
├── qa-report.md              # Phase 6
└── deploy-report.md          # Phase 7
```

## License

MIT
