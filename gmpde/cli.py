"""GMPDE CLI — public interface to the governed execution engine."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from . import __version__
from .blueprint import init, load, validate
from .run_engine import start_run, complete_run, history
from .runtime import get_runtime, ClaudeCodeRuntime

app = typer.Typer(
    name="gmpde",
    help="Governed Multi-Agent Project Development Engine",
    no_args_is_help=True,
)


@app.command()
def version():
    """Print framework version."""
    typer.echo(f"gmpde v{__version__}")


@app.command("init")
def init_project(
    project_name: str = typer.Argument(..., help="Name of the new project")
):
    """Initialize a new project with blueprint.json and runs/ directory."""
    project_dir = Path.cwd() / project_name
    if project_dir.exists():
        typer.echo(f"Error: '{project_name}' already exists.", err=True)
        raise typer.Exit(1)

    project_id = project_name.lower().replace(" ", "-")
    raw_idea = typer.prompt("Describe your idea in one sentence")

    blueprint = init(project_dir, project_id=project_id, project_name=project_name, raw_idea=raw_idea)
    (project_dir / "runs").mkdir(parents=True, exist_ok=True)

    typer.echo(f"\n✅ Project '{project_name}' initialized.")
    typer.echo(f"   Directory : {project_dir}")
    typer.echo(f"   Blueprint : {project_dir / 'blueprint.json'}")
    typer.echo(f"\nNext: cd {project_name} && gmpde validate")


@app.command("validate")
def validate_blueprint():
    """Validate blueprint.json in the current directory."""
    project_dir = Path.cwd()
    try:
        blueprint = load(project_dir)
    except FileNotFoundError:
        typer.echo("Error: No blueprint.json found. Run 'gmpde init <name>' first.", err=True)
        raise typer.Exit(1)

    errors = validate(blueprint)
    if errors:
        typer.echo("🚫 Blueprint validation FAILED:")
        for e in errors:
            typer.echo(f"   • {e}")
        raise typer.Exit(1)

    typer.echo(f"✅ Blueprint valid — project: {blueprint['project_name']} (phase {blueprint['current_phase']})")


@app.command("status")
def status():
    """Show current project status — phase, gate, last run."""
    project_dir = Path.cwd()
    try:
        blueprint = load(project_dir)
    except FileNotFoundError:
        typer.echo(typer.style("No blueprint.json found.", fg=typer.colors.RED))
        raise typer.Exit(1)

    errors = validate(blueprint)

    phase_labels = {
        0: "Problem Clarity", 1: "Research", 2: "Design",
        3: "Planning", 4: "Review", 5: "Development",
        6: "Testing", 7: "Deployment", 8: "Maintenance"
    }
    gate_colors = {
        "pass": typer.colors.GREEN, "pass_with_notes": typer.colors.YELLOW,
        "fail": typer.colors.RED, "complete": typer.colors.GREEN,
        "in_progress": typer.colors.CYAN, "pending": typer.colors.WHITE,
        "failed": typer.colors.RED,
    }

    typer.echo(f"\n{'─'*50}")
    typer.echo(typer.style(f"  {blueprint['project_name']}", bold=True) +
               typer.style(f"  v{blueprint['pipeline_version']}", fg=typer.colors.BRIGHT_BLACK))
    typer.echo(f"{'─'*50}")

    phase_status = blueprint.get("phase_status", {})
    current = blueprint.get("current_phase", 0)
    for i in range(9):
        st = phase_status.get(str(i), "pending")
        label = phase_labels.get(i, f"Phase {i}")
        prefix = "▶ " if i == current else "  "
        color = gate_colors.get(st, typer.colors.WHITE)
        typer.echo(f"{prefix}Phase {i}: {label:<20} " +
                   typer.style(st.upper(), fg=color))

    # Freeze gate
    fg = blueprint.get("freeze_gate", {})
    fg_status = fg.get("status", "locked")
    fg_color = typer.colors.GREEN if fg_status == "approved" else typer.colors.YELLOW
    typer.echo(f"\n  {'🔒 Freeze Gate':<26}" + typer.style(fg_status.upper(), fg=fg_color))

    # Last run
    runs = history(project_dir)
    if runs:
        last = runs[-1]
        typer.echo(f"  {'Last run':<26}{last['run_id']} | {last.get('gate_result','?')}")

    # Validation
    if errors:
        typer.echo(f"\n" + typer.style(f"  ⚠ {len(errors)} validation error(s)", fg=typer.colors.RED))
    else:
        typer.echo(f"\n  " + typer.style("✓ Blueprint valid", fg=typer.colors.GREEN))

    # Runtime
    rt_status = typer.style("available", fg=typer.colors.GREEN) if ClaudeCodeRuntime().is_available() \
        else typer.style("not found (simulated mode)", fg=typer.colors.YELLOW)
    typer.echo(f"  Claude runtime: {rt_status}")
    typer.echo(f"{'─'*50}\n")


@app.command("history")
def show_history():
    """Show run history for the current project."""
    project_dir = Path.cwd()
    runs = history(project_dir)

    if not runs:
        typer.echo("No runs yet.")
        return

    typer.echo(f"\n{'RUN ID':<12} {'PHASE':<7} {'AGENT':<22} {'STATUS':<12} {'GATE':<18} COMPLETED")
    typer.echo("─" * 90)
    for r in runs:
        completed = r.get("completed_at", "")[:19] if r.get("completed_at") else "in progress"
        typer.echo(
            f"{r['run_id']:<12} {str(r.get('phase','?')):<7} {r.get('agent','?'):<22} "
            f"{r.get('status','?'):<12} {r.get('gate_result','?'):<18} {completed}"
        )
    typer.echo(f"\nTotal runs: {len(runs)}")


@app.command()
def run(
    phase: int = typer.Argument(..., help="Phase number to execute (0-8)"),
    runtime: str = typer.Option("claude", help="Runtime adapter: claude | simulated"),
):
    """Execute a phase using the configured runtime adapter."""
    project_dir = Path.cwd()

    try:
        blueprint = load(project_dir)
    except FileNotFoundError:
        typer.echo("Error: No blueprint.json found. Run 'gmpde init <name>' first.", err=True)
        raise typer.Exit(1)

    from .runtime import PHASE_AGENTS
    agent_name = PHASE_AGENTS.get(phase, "unknown")

    try:
        run_id = start_run(project_dir, phase=phase, agent=agent_name, trigger="cli")
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    typer.echo(f"▶  Run started: {run_id} | phase={phase} | agent={agent_name} | runtime={runtime}")

    rt = get_runtime(prefer=runtime)
    rt_name = type(rt).__name__
    typer.echo(f"   Using: {rt_name}")

    try:
        output, gate_result = rt.execute(phase, blueprint, project_dir)
        complete_run(project_dir, run_id, gate_result=gate_result, output=output)
        typer.echo(f"✅ Run complete: {run_id} | gate={gate_result}")
        if output:
            typer.echo(f"\n{output}")
    except ValueError as e:
        typer.echo(f"🚫 {e}", err=True)
        raise typer.Exit(1)


