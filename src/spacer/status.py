import os
import click
import yaml

PHASE_ORDER = ["ideation", "outlining", "drafting", "revision", "submission"]

NEXT_ACTIONS = {
    "ideation": "Run a literature survey: `spacer bib search \"your topic\"`",
    "outlining": "Create section outlines in paper/plan/",
    "drafting": "Write sections in paper/sections/",
    "revision": "Review and polish your draft",
    "submission": "Final formatting and compliance check",
}

@click.command()
def status_cmd():
    """Show project status."""
    if not os.path.exists("spacer.yaml"):
        click.echo("No spacer.yaml found. Run `spacer init` first.")
        raise SystemExit(1)

    with open("spacer.yaml") as f:
        cfg = yaml.safe_load(f)

    phase = cfg.get("phase", "?")
    status = cfg.get("phase_status", "?")
    click.echo(f"Phase: {phase} ({status})")

    # Framing
    framing = cfg.get("framing", {})
    filled = {k: v for k, v in framing.items() if v}
    if filled:
        click.echo("\nMcEnerney Framing:")
        for k, v in filled.items():
            click.echo(f"  {k}: {v}")

    # Phase checklist
    checklist = cfg.get(phase, {})
    if isinstance(checklist, dict):
        click.echo(f"\n{phase.title()} Checklist:")
        for k, v in checklist.items():
            mark = "✓" if v else "○"
            click.echo(f"  {mark} {k.replace('_', ' ')}")

    # Next action
    click.echo(f"\nNext: {NEXT_ACTIONS.get(phase, 'Keep going!')}")
