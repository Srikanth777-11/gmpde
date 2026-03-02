---
name: pipeline
description: Launch the hierarchical agent pipeline for a new idea or feature. Usage: /pipeline [your idea description]
---

# Pipeline Launch Command

The user wants to start the full hierarchical agent pipeline. Use the orchestrator agent to coordinate the entire process.

**Instructions:**
1. Take the user's idea/description provided as the argument
2. Launch the orchestrator agent with the idea
3. The orchestrator will manage all phases automatically
4. Ensure the `docs/` directory structure exists before starting

**Launch prompt for orchestrator:**
```
PIPELINE START
Idea: $ARGUMENTS
Action:
1. Create docs/ directory structure if it doesn't exist (including docs/reviews/, docs/task-reports/, docs/test-reports/)
2. Initialize docs/decision-log.md if it doesn't exist
3. Begin Phase 0 (Problem Clarification) — dispatch problem-clarifier agent
4. Report pipeline plan to the user before continuing to Phase 1
5. After Phase 4, STOP and present design summary. Tell user to run /approve-design before implementation begins
6. Show phase status dashboard after each phase completes
```
