"""SPACER interactive chat — shells out to claude/codex CLI."""

import shlex
from datetime import datetime
from pathlib import Path

import click
from prompt_toolkit import PromptSession

from .auth import get_backend
from .bib import _s2_fields, _s2_get
from .llm import brain, hands
from .status import (
    advance_sub_step,
    format_phase_info,
    format_status,
    get_current_sub_step,
    get_phase,
    get_phase_status,
    load_spacer_config,
)

SYSTEM_PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "system.md"
MAX_SUPPLY_CHARS = 12000


def _build_system_prompt(config_path):
    """Build system prompt from template + current state."""
    template = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    cfg = load_spacer_config(config_path)

    phase = cfg.get("phase", "unknown")
    phase_status = cfg.get("phase_status", "unknown")
    sub_step = get_current_sub_step(cfg)

    # Load constitution if exists
    constitution = ""
    const_path = Path("constitution/ideation.md")
    if const_path.exists():
        constitution = const_path.read_text(encoding="utf-8")

    prompt = template.replace("[[PHASE]]", phase)
    prompt = prompt.replace("[[PHASE_STATUS]]", phase_status)
    prompt = prompt.replace("[[SUB_STEP]]", sub_step or "none")
    prompt = prompt.replace("[[CONSTITUTION]]", constitution or "(none yet)")

    return prompt


def _save_transcript(history, phase):
    """Save conversation to markdown file."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(f"notes/{phase}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"discussion-{ts}.md"

    lines = [f"# SPACER Discussion — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    for role, text in history:
        header = "## You" if role == "user" else "## SPACER"
        lines.append(f"\n{header}\n{text}\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def _handle_slash(cmd_line, history, config_path):
    """Handle slash commands. Returns (response_text, should_quit)."""
    parts = shlex.split(cmd_line)
    cmd = parts[0].lower() if parts else ""

    if cmd in ("/quit", "/exit"):
        cfg = load_spacer_config(config_path)
        phase = cfg.get("phase", "ideation")
        path = _save_transcript(history, phase)
        return f"Saved transcript to {path}. Goodbye!", True

    elif cmd == "/status":
        return format_status(config_path), False

    elif cmd == "/phase":
        return format_phase_info(config_path), False

    elif cmd == "/next":
        msg = advance_sub_step(config_path)
        return msg, False

    elif cmd == "/save":
        cfg = load_spacer_config(config_path)
        phase = cfg.get("phase", "ideation")
        path = _save_transcript(history, phase)
        return f"Saved to {path}", False

    elif cmd == "/supply":
        if len(parts) < 2:
            return "Usage: /supply <filepath>", False
        fpath = Path(parts[1])
        if not fpath.exists():
            return f"File not found: {fpath}", False
        text = fpath.read_text(encoding="utf-8")
        if len(text) > MAX_SUPPLY_CHARS:
            text = text[:MAX_SUPPLY_CHARS] + "\n...(truncated)"
        return f"📄 Loaded {fpath.name} ({len(text)} chars). Content added to context.", False

    elif cmd == "/bib":
        if len(parts) < 3 or parts[1] != "search":
            return "Usage: /bib search \"query\"", False
        query = " ".join(parts[2:])
        try:
            params = {"query": query, "limit": 5, "fields": _s2_fields()}
            resp = _s2_get("https://api.semanticscholar.org/graph/v1/paper/search", params)
            if resp is None:
                return "Search failed (rate limited)", False
            data = resp.json().get("data", [])
            if not data:
                return "No results found.", False
            lines = []
            for p in data:
                authors = ", ".join(a.get("name", "?") for a in (p.get("authors") or [])[:3])
                year = p.get("year", "?")
                title = p.get("title", "?")
                cite = p.get("citationCount", 0)
                lines.append(f"• [{year}] {title}\n  {authors} (citations: {cite})")
            return "\n".join(lines), False
        except Exception as e:
            return f"Search error: {e}", False

    elif cmd == "/constitute":
        return "CONSTITUTE_REQUEST", False

    elif cmd == "/review":
        # Show existing drafts
        sections_dir = Path("paper/sections")
        if not sections_dir.exists():
            return "No drafts yet (paper/sections/ is empty)", False
        files = sorted(sections_dir.glob("*.tex"))
        if not files:
            return "No .tex files in paper/sections/ yet.", False
        lines = ["Existing drafts:"]
        for f in files:
            size = f.stat().st_size
            lines.append(f"  • {f.name} ({size} bytes)")
        lines.append("\nUse /supply paper/sections/<file>.tex to load a draft for discussion.")
        return "\n".join(lines), False

    else:
        return f"Unknown command: {cmd}\nCommands: /status /phase /next /bib /supply /constitute /review /save /quit", False


@click.command("chat")
def chat_cmd():
    """Start interactive SPACER chat session."""
    config_path = "spacer.yaml"
    cfg = load_spacer_config(config_path)
    if cfg is None:
        click.echo("No spacer.yaml found. Run `spacer init` first.")
        raise SystemExit(1)

    backend = get_backend()
    if not backend:
        click.echo("No backend configured. Run `spacer auth` first.")
        raise SystemExit(1)

    phase = cfg.get("phase", "unknown")
    sub_step = get_current_sub_step(cfg) or "starting"

    click.echo(f"╔══════════════════════════════════════════════╗")
    click.echo(f"║  SPACER — Phase: {phase} ({sub_step})")
    click.echo(f"║  Commands: /status /phase /bib /supply")
    click.echo(f"║            /constitute /review /next /save /quit")
    click.echo(f"╚══════════════════════════════════════════════╝")
    click.echo()

    history = []  # list of (role, text)
    supplied_context = []  # extra context from /supply

    # Build system prompt
    system_prompt = _build_system_prompt(config_path)

    # Message history for API calls
    api_messages = []

    # Initial greeting
    click.echo("SPACER: Starting up... let me review the project state.")
    try:
        api_messages.append({"role": "user", "content": "I just opened the chat. Briefly greet me and acknowledge the current phase. What should we work on?"})
        greeting = brain(system_prompt, api_messages)
        click.echo(f"\nSPACER: {greeting}\n")
        api_messages.append({"role": "assistant", "content": greeting})
        history.append(("assistant", greeting))
    except Exception as e:
        click.echo(f"\n(Could not get initial greeting: {e})\n")

    session = PromptSession()

    while True:
        try:
            user_input = session.prompt("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            cfg = load_spacer_config(config_path)
            phase = cfg.get("phase", "ideation")
            path = _save_transcript(history, phase)
            click.echo(f"\nSaved transcript to {path}. Goodbye!")
            break

        if not user_input:
            continue

        # Handle slash commands
        if user_input.startswith("/"):
            response, should_quit = _handle_slash(user_input, history, config_path)

            if response == "CONSTITUTE_REQUEST":
                # Ask LLM to generate constitution from discussion
                click.echo("\nSPACER: Generating constitution from our discussion...\n")
                const_prompt = (
                    "Based on our discussion so far, generate a constitution document for this research project. "
                    "Include: McEnerney framing (readers, instability, cost, solution), terminology definitions, "
                    "scope boundaries, positioning decisions, and key papers with their roles. "
                    "Format as markdown suitable for constitution/ideation.md"
                )
                api_messages.append({"role": "user", "content": const_prompt})
                try:
                    constitution = brain(system_prompt, api_messages)
                    click.echo(f"SPACER:\n{constitution}\n")
                    api_messages.append({"role": "assistant", "content": constitution})
                    history.append(("assistant", constitution))

                    # Offer to save
                    save = click.confirm("Save to constitution/ideation.md?", default=True)
                    if save:
                        Path("constitution").mkdir(exist_ok=True)
                        Path("constitution/ideation.md").write_text(constitution, encoding="utf-8")
                        click.echo("✓ Saved constitution/ideation.md")
                except Exception as e:
                    click.echo(f"Error: {e}")
                continue

            click.echo(f"\n{response}\n")
            if should_quit:
                break
            continue

        # Regular message — send to brain
        history.append(("user", user_input))
        api_messages.append({"role": "user", "content": user_input})

        # Trim API messages to avoid token limits (keep last 40)
        if len(api_messages) > 40:
            api_messages = api_messages[-40:]

        # Refresh system prompt (in case constitution was added)
        system_prompt = _build_system_prompt(config_path)

        try:
            response = brain(system_prompt, api_messages)
            click.echo(f"\nSPACER: {response}\n")
            api_messages.append({"role": "assistant", "content": response})
            history.append(("assistant", response))
        except Exception as e:
            click.echo(f"\nError: {e}\n")
