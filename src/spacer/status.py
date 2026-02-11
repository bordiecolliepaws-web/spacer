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


def load_spacer_config(config_path="spacer.yaml"):
    """Load spacer.yaml config."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(config_path)

    with open(config_path) as f:
        cfg = yaml.safe_load(f) or {}
    if not isinstance(cfg, dict):
        raise ValueError("spacer.yaml must contain a YAML mapping.")
    return cfg


def save_spacer_config(cfg, config_path="spacer.yaml"):
    """Persist spacer config back to disk."""
    with open(config_path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


def get_phase(cfg):
    return cfg.get("phase", "?")


def get_phase_status(cfg):
    return cfg.get("phase_status", "?")


def get_phase_checklist(cfg):
    phase = get_phase(cfg)
    checklist = cfg.get(phase, {})
    if isinstance(checklist, dict):
        return checklist
    return {}


def get_current_sub_step(cfg):
    checklist = get_phase_checklist(cfg)
    if not checklist:
        return None
    for key, value in checklist.items():
        if not bool(value):
            return key
    return "complete"


def format_phase_info(cfg):
    """Format current phase and checklist summary."""
    phase = get_phase(cfg)
    status = get_phase_status(cfg)
    sub_step = get_current_sub_step(cfg)

    lines = [f"Phase: {phase} ({status})"]
    if sub_step == "complete":
        lines.append("Sub-step: complete")
    elif sub_step:
        lines.append(f"Sub-step: {sub_step.replace('_', ' ')}")

    checklist = get_phase_checklist(cfg)
    if checklist:
        lines.append("")
        lines.append(f"{phase.title()} Checklist:")
        for key, value in checklist.items():
            mark = "✓" if value else "○"
            lines.append(f"  {mark} {key.replace('_', ' ')}")
    return "\n".join(lines)


def format_status(cfg):
    """Format full status output."""
    phase = get_phase(cfg)
    lines = [format_phase_info(cfg)]

    # Framing
    framing = cfg.get("framing", {})
    filled = {k: v for k, v in framing.items() if v}
    if filled:
        lines.append("")
        lines.append("McEnerney Framing:")
        for key, value in filled.items():
            lines.append(f"  {key}: {value}")

    # Next action
    lines.append("")
    lines.append(f"Next: {NEXT_ACTIONS.get(phase, 'Keep going!')}")
    return "\n".join(lines)


def advance_sub_step(config_path="spacer.yaml"):
    """Mark the current sub-step as complete."""
    cfg = load_spacer_config(config_path)
    phase = get_phase(cfg)
    checklist = get_phase_checklist(cfg)
    if not checklist:
        return False, f"No checklist found for phase '{phase}'.", cfg

    for key, value in checklist.items():
        if not bool(value):
            checklist[key] = True
            message = f"Marked sub-step complete: {key.replace('_', ' ')}."
            if all(bool(v) for v in checklist.values()):
                cfg["phase_status"] = "review"
                message += " All checklist items are complete; phase_status set to review."
            save_spacer_config(cfg, config_path)
            return True, message, cfg

    return False, "All sub-steps are already complete.", cfg

@click.command()
def status_cmd():
    """Show project status."""
    if not os.path.exists("spacer.yaml"):
        click.echo("No spacer.yaml found. Run `spacer init` first.")
        raise SystemExit(1)

    cfg = load_spacer_config("spacer.yaml")
    click.echo(format_status(cfg))
