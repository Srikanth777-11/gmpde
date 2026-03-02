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
Action: Assess complexity, create pipeline plan, begin Phase 1 (Research).
Create docs/ directory structure if it doesn't exist.
Report your pipeline plan to the user before beginning execution.
```
