# Changelog

All notable changes to GMPDE are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-03-02

Initial release of GMPDE — Governed Multi-Agent Project Development Engine.

### Added

**Governance Core**
- `blueprint.json` — canonical machine-readable project state with JSON Schema validation
- Phase gate system — no phase advances without predecessor artifact
- Freeze gate — hard stop before implementation, requires explicit `/approve-design`
- Decision log (`docs/decision-log.md`) — append-only, immutable institutional memory with DL-NNN IDs

**Run Engine** (`gmpde/run_engine.py`)
- `start_run()` — creates run directory, captures before-snapshot
- `complete_run()` — enforces contracts, validates mutations, advances phase, writes after-snapshot
- `fail_run()` — marks run as failed with reason
- `replay()` — restores blueprint to pre-run state for debugging
- `history()` — returns all completed runs from atomic run index
- Atomic index writes via temp file + `shutil.move()`
- Run IDs in `run-NNNN` format

**Agent Output Contracts** (`gmpde/contracts.py`)
- `parse_agent_output()` — extracts structured `gmpde-output` block from agent response
- `validate_mutations()` — enforces per-phase mutation scope (`PHASE_ALLOWED_MUTATIONS`)
- `validate_decisions()` — enforces decision log append-only semantics
- `validate_transition()` — validates phase transitions and freeze gate requirements
- Strict mode toggle via `config.strict_contracts` in blueprint

**Runtime Abstraction** (`gmpde/runtime.py`)
- `AgentRuntime` ABC — common interface for all runtimes
- `ClaudeCodeRuntime` — invokes agents via Claude Code CLI
- `SimulatedRuntime` — deterministic simulation for testing without AI calls
- `get_runtime()` factory — auto-falls back to SimulatedRuntime if Claude unavailable

**CLI** (`gmpde/cli.py`)
- `gmpde version` — show version
- `gmpde init <name>` — initialize new project with blueprint.json
- `gmpde validate` — validate current project blueprint
- `gmpde status` — colored phase dashboard with freeze gate state, last run, runtime availability
- `gmpde history` — list completed runs
- `gmpde run <phase>` — execute a phase (`--runtime claude|simulated`)

**Schema**
- `schema/blueprint.schema.json` — full JSON Schema for blueprint validation
- `schema/blueprint.template.json` — blank project state template
- `schema/run_metadata.template.json` — run record template
- `schema/run_index.template.json` — run index template

**Tests** (29 unit tests)
- `tests/test_blueprint.py` — blueprint lifecycle: init, validate, advance_phase
- `tests/test_contracts.py` — contract enforcement: parsing, mutations, decisions, transitions
- `tests/test_run_engine.py` — run lifecycle: start, complete, fail, replay, history

**CI**
- GitHub Actions workflow on Python 3.9, 3.11, 3.12
- Install + test + CLI smoke test on every push to main

**Documentation**
- `docs/architecture.md` — system overview, agent table, gate criteria, token limits
- `docs/blueprint-schema.md` — human-readable blueprint field reference
- `docs/run-engine.md` — run engine and replay specification
- `README.md` — install, usage, agent hierarchy, governance features

### Agent Hierarchy

13 agents across 9 phases (0–8), coordinated by the orchestrator (Opus).
All agents follow token conservation protocol and communicate only through artifacts.

---

[1.0.0]: https://github.com/yourusername/gmpde/releases/tag/v1.0.0
