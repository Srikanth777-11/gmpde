"""Runtime — abstracted agent execution layer.

CLI and engine never know which runtime is used.
Adapters implement the AgentRuntime interface.
"""
from __future__ import annotations

import json
import subprocess
import shutil
from abc import ABC, abstractmethod
from pathlib import Path


# Phase → agent name mapping
PHASE_AGENTS = {
    0: "problem-clarifier",
    1: "idea-researcher",
    2: "architect",
    3: "project-planner",
    4: "doc-reviewer",
    5: "implementer",
    6: "test-writer",
    7: "deployer",
    8: "monitor",
}


class AgentRuntime(ABC):
    """Base interface. All adapters must implement this."""

    @abstractmethod
    def execute(self, phase: int, blueprint: dict, project_dir: Path) -> tuple[str, str]:
        """
        Execute an agent for the given phase.
        Returns (output: str, gate_result: str)
        gate_result: 'pass' | 'pass_with_notes' | 'fail'
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this runtime can be used in the current environment."""


class SimulatedRuntime(AgentRuntime):
    """Fallback — no real agent, returns mock output. Always available."""

    def execute(self, phase: int, blueprint: dict, project_dir: Path) -> tuple[str, str]:
        agent = PHASE_AGENTS.get(phase, "unknown")
        output = f"[SIMULATED] Phase {phase} executed by {agent}."
        return (output, "pass")

    def is_available(self) -> bool:
        return True


class ClaudeCodeRuntime(AgentRuntime):
    """Adapter for Claude Code CLI (`claude` binary)."""

    def _find_claude(self) -> str | None:
        return shutil.which("claude")

    def _agent_path(self, phase: int) -> Path | None:
        agent_name = PHASE_AGENTS.get(phase)
        if not agent_name:
            return None
        for parent in [Path.cwd(), *Path.cwd().parents]:
            candidate = parent / ".claude" / "agents" / f"{agent_name}.md"
            if candidate.exists():
                return candidate
        return None

    def execute(self, phase: int, blueprint: dict, project_dir: Path) -> tuple[str, str]:
        claude = self._find_claude()
        if not claude:
            raise RuntimeError("Claude Code CLI not found.")

        agent_name = PHASE_AGENTS.get(phase)
        if not agent_name:
            raise ValueError(f"No agent mapped for phase {phase}")

        problem = blueprint.get("problem_statement", {})
        context = {
            "project_id": blueprint["project_id"],
            "project_name": blueprint["project_name"],
            "current_phase": phase,
            "raw_idea": problem.get("raw_idea", ""),
            "blueprint_path": str(project_dir / "blueprint.json"),
        }

        prompt = (
            f"PHASE: {phase}\n"
            f"AGENT: {agent_name}\n"
            f"PROJECT_DIR: {project_dir}\n"
            f"CONTEXT: {json.dumps(context)}\n\n"
            f"Execute your designated role. Read {project_dir / 'blueprint.json'} "
            f"for full project state. Update it with your phase outputs."
        )

        result = subprocess.run(
            [claude, "--agent", agent_name, "--print", prompt],
            capture_output=True, text=True, cwd=str(project_dir),
        )

        output = result.stdout.strip()
        if result.returncode != 0:
            return (f"Agent execution failed:\n{result.stderr.strip()}", "fail")

        return (output, _detect_gate(output))

    def is_available(self) -> bool:
        return self._find_claude() is not None


def get_runtime(prefer: str = "claude") -> AgentRuntime:
    """
    Return the best available runtime.
    prefer: 'claude' | 'simulated'
    Falls back to SimulatedRuntime if preferred is unavailable.
    """
    candidates: dict[str, AgentRuntime] = {
        "claude": ClaudeCodeRuntime(),
        "simulated": SimulatedRuntime(),
    }
    runtime = candidates.get(prefer, SimulatedRuntime())
    if runtime.is_available():
        return runtime
    return SimulatedRuntime()


def _detect_gate(output: str) -> str:
    lower = output.lower()
    if "🚫 fail" in lower or "verdict: fail" in lower:
        return "fail"
    if "⚠️" in lower or "pass_with_notes" in lower or "pass with notes" in lower:
        return "pass_with_notes"
    return "pass"
