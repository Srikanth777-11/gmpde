# Run Engine & Replay

## Overview

Every agent execution creates a run. Runs are project-scoped — each project carries its own full execution history.

## Structure (per project)

```
my-project/
├── blueprint.json          # Current canonical state
├── runs/
│   ├── run-index.json      # Index of all runs
│   ├── run-001/
│   │   ├── run_metadata.json       # Run context and result
│   │   ├── blueprint.before.json   # State snapshot before agent ran
│   │   ├── blueprint.after.json    # State snapshot after agent ran
│   │   └── agent_outputs/
│   │       └── output.md           # Raw agent output
│   └── run-002/
│       └── ...
```

## Run Lifecycle

1. **Before agent dispatch** — Orchestrator snapshots `blueprint.json` → `runs/run-NNN/blueprint.before.json`
2. **Agent executes** — Reads blueprint, performs work, writes output
3. **After agent completes** — Orchestrator snapshots updated `blueprint.json` → `runs/run-NNN/blueprint.after.json`
4. **Run metadata written** — Status, gate result, timestamps recorded
5. **Index updated** — Entry appended to `runs/run-index.json`

## Run ID Format

Sequential: `run-001`, `run-002`, `run-003`...
Check `run-index.json` for last ID before creating new run.

## Replay

To replay a phase, copy `blueprint.before.json` from the target run back to `blueprint.json`, then re-dispatch the agent.

## Diff

Compare `blueprint.before.json` vs `blueprint.after.json` to see exactly what an agent changed.

## Gate Results

| Result | Meaning |
|--------|---------|
| `pass` | Phase complete, advance |
| `pass_with_notes` | Advance with non-blocking issues logged |
| `fail` | Return to previous phase |
| `awaiting_user` | Freeze gate — waiting for /approve-design |
| `null` | Run in progress |
