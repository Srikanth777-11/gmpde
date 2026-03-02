---
name: quick-task
description: Run a single agent directly without the full pipeline. Usage: /quick-task [agent-name] [task description]
---

# Quick Task Command

Run a single agent without the full pipeline orchestration. Useful for:
- Running just the researcher on an idea
- Getting just an architecture review
- Writing tests for existing code
- Quick code optimization pass

**Instructions:**
1. Parse the first argument as the agent name
2. Pass remaining arguments as the task description
3. Launch the specified agent directly with the task

**Available agents:** idea-researcher, tech-scout, architect, project-planner, doc-reviewer, implementer, code-optimizer, test-writer, qa-validator, deployer, monitor

**Launch:**
```
Use the $1 agent with this task: $ARGUMENTS
```
