---
name: approve-design
description: "User freeze gate — approve the design and allow implementation to begin. Usage: /approve-design [optional notes]"
---

# Design Approval — User Freeze Gate

The user is issuing explicit approval to move from design/planning phases into implementation.

**This is a GOVERNANCE CONTROL. Without this command, the pipeline MUST NOT begin Phase 5 (Development).**

## Pre-Approval Checklist

Before approving, verify ALL of the following exist and have been reviewed:

1. **Problem Statement** — `docs/problem-statement.md` exists and is clear
2. **Research Brief** — `docs/research-brief.md` exists with ✅ PASS review
3. **Architecture Decision Record** — `docs/adr.md` exists with ✅ PASS review
4. **Project Plan** — `docs/project-plan.md` exists with ✅ PASS review
5. **Decision Log** — `docs/decision-log.md` has entries from all phases

## What to Do

1. Read all documents listed above
2. Present a **concise summary** to the user:
   - Problem being solved (from problem-statement.md)
   - Architecture chosen (from adr.md)
   - Number of tasks planned (from project-plan.md)
   - Key decisions made (from decision-log.md)
   - Any ⚠️ PASS WITH NOTES items from reviews
3. Ask the user to confirm: **"Proceed to implementation?"**
4. If user confirms:
   - Write `APPROVED` status to `docs/design-approval.md` with timestamp and any user notes
   - Signal to the orchestrator that Phase 5 may begin
5. If user does NOT confirm:
   - Ask what needs to change
   - Route feedback to the orchestrator for the appropriate phase

## Design Approval Record

Write to `docs/design-approval.md`:

```markdown
# Design Approval
**Date:** [date]
**Status:** APPROVED / REJECTED
**Approved by:** User

## Summary Reviewed
- Problem: [one line from problem-statement.md]
- Architecture: [one line from adr.md]
- Tasks: [count from project-plan.md]
- Open concerns: [any PASS WITH NOTES items]

## User Notes
$ARGUMENTS

## Gate Result
Implementation Phase 5 is now UNLOCKED.
```

## Critical Rules
- This gate is MANDATORY. The orchestrator must check for `docs/design-approval.md` with `APPROVED` status before dispatching ANY implementation tasks
- If the user runs `/approve-design` but artifacts are missing, DO NOT approve — list what's missing
- The user can re-run `/approve-design` after changes to update the approval
