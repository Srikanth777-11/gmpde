# GMPDE Architecture

## System Overview

GMPDE is a governed multi-agent pipeline that coordinates 13 specialized AI agents across 9 phases (0-8) to take a raw idea through structured development.

## Core Principles

1. **Governance over speed** — No phase advances without artifacts and approval
2. **Separation of concerns** — Each agent has one job, no scope creep
3. **Token conservation** — Compressed context, scoped reading, output limits
4. **Human control** — Freeze gate before implementation, max 2 retries then escalate
5. **Traceability** — Decision log records every significant choice

## Pipeline Flow

```
Idea → Phase 0 (Clarify) → Phase 1 (Research) → Phase 2 (Design) → Phase 3 (Plan)
    → Phase 4 (Review) → FREEZE GATE (User Approval)
    → Phase 5 (Implement) → Phase 6 (Test) → Phase 7 (Deploy) → Phase 8 (Monitor)
```

## Communication Model

- Agents NEVER communicate directly with each other
- All coordination flows through the orchestrator
- Agents communicate via document artifacts in `docs/`
- Orchestrator uses standardized task dispatch format

## Model Assignment Strategy

- **Opus** (complex reasoning): orchestrator, architect
- **Sonnet** (focused execution): problem-clarifier, idea-researcher, project-planner, doc-reviewer, implementer, code-optimizer, test-writer, qa-validator, deployer
- **Haiku** (quick checks): tech-scout, monitor

## Quality Gates

| Phase | Gate Criteria | Failure Action |
|-------|--------------|----------------|
| 0 - Problem | No open blockers, scope defined | Ask user to clarify |
| 1 - Research | Brief covers feasibility + approach | Re-research with refined scope |
| 2 - Design | ADR complete, no contradictions | Back to architect with gaps |
| 3 - Planning | Tasks atomic, estimable, ordered | Re-decompose oversized tasks |
| 4 - Review | No blocking issues | Route blockers to design/planning |
| FREEZE | User runs /approve-design | Present summary, wait |
| 5 - Development | Compiles + lint clean | Back to implementer with errors |
| 6 - Testing | Tests pass + coverage > 80% | Back to test-writer for gaps |
| 7 - Deployment | Health checks pass | Rollback + diagnose |

## Token Conservation Protocol

| Agent | Max Output | Max Files |
|-------|-----------|-----------|
| problem-clarifier | 400 words | 5 |
| idea-researcher | 500 words | 10 |
| tech-scout | 300 words | 5 |
| architect | 800 words | 8 |
| project-planner | 600 words | 5 |
| doc-reviewer | 400 words | artifact + 3 |
| implementer | report only | 5/task |
| code-optimizer | 200 words | 5 |
| test-writer | code + 300 words | 4/task |
| qa-validator | 400 words | 4/task |
| deployer | 300 words | 5 |
| monitor | 200 words | 3 |
