import os
import io
import sys
import shlex
import click
import yaml
from datetime import datetime
from pathlib import Path

from .auth import get_api_key


def _load_config():
    if os.path.exists("spacer.yaml"):
        with open("spacer.yaml") as f:
            return yaml.safe_load(f) or {}
    return {}


def _build_system_prompt(cfg):
    phase = cfg.get("phase", "unknown")
    phase_status = cfg.get("phase_status", "unknown")

    # Determine substep
    checklist = cfg.get(phase, {})
    substep = "none"
    if isinstance(checklist, dict):
        for k, v in checklist.items():
            if not v:
                substep = k.replace("_", " ")
                break

    # Load template
    template_path = Path(__file__).parent / "prompts" / "system.md"
    if template_path.exists():
        template = template_path.read_text()
    else:
        template = "You are SPACER, an AI research collaborator.\n\nPhase: {phase} ({phase_status})\nSub-step: {substep}\n\n{constitution}"

    # Constitution
    constitution = ""
    if os.path.exists("constitution.md"):
        constitution = f"## Constitution\n{Path('constitution.md').read_text()}"

    return template.format(
        phase=phase,
        phase_status=phase_status,
        substep=substep,
        constitution=constitution,
    )


def _handle_slash(cmd_str, history, cfg, client, model):
    """Handle slash commands. Returns (response_text, should_quit)."""
    parts = shlex.split(cmd_str) if cmd_str.strip() else [""]
    cmd = parts[0].lower() if parts else ""

    if cmd == "/quit":
        return None, True

    if cmd == "/save":
        _save_conversation(history, cfg)
        return "💾 Conversation saved.", False

    if cmd == "/status":
        from .status import status_cmd
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            status_cmd.main(standalone_mode=False)
        except SystemExit:
            pass
        sys.stdout = old_stdout
        return buf.getvalue() or "No status available.", False

    if cmd == "/phase":
        phase = cfg.get("phase", "unknown")
        status = cfg.get("phase_status", "unknown")
        checklist = cfg.get(phase, {})
        lines = [f"Phase: {phase} ({status})"]
        if isinstance(checklist, dict):
            for k, v in checklist.items():
                mark = "✓" if v else "○"
                lines.append(f"  {mark} {k.replace('_', ' ')}")
        return "\n".join(lines), False

    if cmd == "/bib":
        from .bib import bib_group
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            bib_group.main(parts[1:], standalone_mode=False)
        except SystemExit:
            pass
        sys.stdout = old_stdout
        return buf.getvalue() or "No results.", False

    if cmd == "/supply":
        if len(parts) < 2:
            return "Usage: /supply <filepath>", False
        fpath = parts[1]
        if not os.path.exists(fpath):
            return f"File not found: {fpath}", False
        content = Path(fpath).read_text()
        # Add as user message context
        history.append({
            "role": "user",
            "content": f"[File: {fpath}]\n\n{content}",
        })
        return f"📄 Added {fpath} to context ({len(content)} chars).", False

    if cmd == "/constitute":
        # Ask the agent to generate a constitution
        history.append({
            "role": "user",
            "content": "Based on our discussion so far, generate a research constitution — a concise document capturing our research question, approach, key principles, and constraints. Format it as markdown suitable for constitution.md.",
        })
        resp = _call_llm(client, model, history, _build_system_prompt(cfg))
        history.append({"role": "assistant", "content": resp})
        return resp, False

    if cmd == "/review":
        return "Review mode not yet implemented.", False

    if cmd == "/next":
        # Advance to next incomplete substep
        phase = cfg.get("phase", "ideation")
        checklist = cfg.get(phase, {})
        if isinstance(checklist, dict):
            for k, v in checklist.items():
                if not v:
                    checklist[k] = True
                    with open("spacer.yaml", "w") as f:
                        yaml.dump(cfg, f, default_flow_style=False)
                    return f"✓ Marked '{k.replace('_', ' ')}' as done.", False
        return "All sub-steps complete.", False

    return f"Unknown command: {cmd}", False


def _call_llm(client, model, history, system_prompt):
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=history,
        )
        return resp.content[0].text
    except Exception as e:
        return f"[Error: {e}]"


def _save_conversation(history, cfg):
    phase = cfg.get("phase", "ideation")
    notes_dir = Path(f"notes/{phase}")
    notes_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    fpath = notes_dir / f"discussion-{ts}.md"

    lines = [f"# SPACER Discussion — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    lines.append(f"Phase: {cfg.get('phase', '?')} ({cfg.get('phase_status', '?')})\n")
    for msg in history:
        role = "Human" if msg["role"] == "user" else "Agent"
        lines.append(f"\n## {role}\n\n{msg['content']}\n")

    fpath.write_text("\n".join(lines))
    click.echo(f"Saved to {fpath}")


@click.command()
def chat_cmd():
    """Interactive chat with SPACER AI agent."""
    api_key = get_api_key()
    if not api_key:
        click.echo("No API key found. Run `spacer auth` first.")
        raise SystemExit(1)

    try:
        import anthropic
    except ImportError:
        click.echo("Install anthropic: pip install anthropic")
        raise SystemExit(1)

    client = anthropic.Anthropic(api_key=api_key)
    model = "claude-sonnet-4-5-20250514"
    cfg = _load_config()
    system_prompt = _build_system_prompt(cfg)
    history = []

    # Try prompt_toolkit, fall back to basic input
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.formatted_text import HTML
        session = PromptSession()
        use_pt = True
    except ImportError:
        session = None
        use_pt = False

    # Header
    phase = cfg.get("phase", "unknown")
    phase_status = cfg.get("phase_status", "unknown")
    click.echo("=" * 60)
    click.echo(f"  SPACER — Phase: {phase} ({phase_status})")
    click.echo(f"  Model: {model}")
    click.echo(f"  Commands: /status /phase /bib /supply /save /quit")
    click.echo("=" * 60)

    # Initial greeting from agent
    history.append({
        "role": "user",
        "content": "I just started a SPACER chat session. Briefly greet me and tell me what phase we're in and how you can help. Keep it to 2-3 sentences.",
    })
    greeting = _call_llm(client, model, history, system_prompt)
    history.append({"role": "assistant", "content": greeting})
    click.echo(f"\n🤖 {greeting}\n")

    while True:
        try:
            if use_pt:
                user_input = session.prompt("You> ")
            else:
                user_input = input("You> ")
        except (EOFError, KeyboardInterrupt):
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            result, should_quit = _handle_slash(user_input, history, cfg, client, model)
            if should_quit:
                _save_conversation(history, cfg)
                click.echo("Goodbye!")
                break
            if result:
                click.echo(f"\n{result}\n")
            continue

        # Regular message
        history.append({"role": "user", "content": user_input})
        click.echo("\n⏳ Thinking...")
        response = _call_llm(client, model, history, system_prompt)
        history.append({"role": "assistant", "content": response})
        click.echo(f"\n🤖 {response}\n")
