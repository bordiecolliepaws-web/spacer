import shlex
from datetime import datetime
from pathlib import Path

import click
from anthropic import Anthropic
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import clear

from .auth import get_anthropic_api_key
from .bib import _s2_fields, _s2_get
from .status import (
    advance_sub_step,
    format_phase_info,
    format_status,
    get_current_sub_step,
    get_phase,
    get_phase_status,
    load_spacer_config,
)

MODEL_NAME = "claude-sonnet-4-5"
SYSTEM_PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "system.md"
MAX_HISTORY_MESSAGES = 60
MAX_SUPPLY_CHARS = 12000
DISPLAY_MESSAGES = 24


def _extract_response_text(response):
    blocks = getattr(response, "content", [])
    parts = []
    for block in blocks:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            parts.append(getattr(block, "text", ""))
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    text = "\n".join(p for p in parts if p).strip()
    return text or "(No response text returned.)"


def _trim_history(history):
    if len(history) > MAX_HISTORY_MESSAGES:
        del history[:-MAX_HISTORY_MESSAGES]


def _build_system_prompt(config_path):
    template = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    cfg = load_spacer_config(config_path)

    phase = get_phase(cfg)
    phase_status = get_phase_status(cfg)
    sub_step = get_current_sub_step(cfg)
    if sub_step is None:
        sub_step_text = "none"
    elif sub_step == "complete":
        sub_step_text = "complete"
    else:
        sub_step_text = sub_step.replace("_", " ")

    constitution_path = Path("constitution/ideation.md")
    if constitution_path.exists():
        constitution_text = constitution_path.read_text(encoding="utf-8", errors="replace").strip()
    else:
        constitution_text = "(No constitution/ideation.md found yet.)"

    return (
        template.replace("[[PHASE]]", str(phase))
        .replace("[[PHASE_STATUS]]", str(phase_status))
        .replace("[[SUB_STEP]]", str(sub_step_text))
        .replace("[[CONSTITUTION]]", constitution_text)
    )


def _ask_model(client, config_path, history, user_text):
    system_prompt = _build_system_prompt(config_path)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1200,
        system=system_prompt,
        messages=history + [{"role": "user", "content": user_text}],
    )
    text = _extract_response_text(response)
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": text})
    _trim_history(history)
    return text


def _render_header(cfg):
    phase = get_phase(cfg)
    status = get_phase_status(cfg)
    sub_step = get_current_sub_step(cfg)
    if sub_step is None:
        sub_step_label = "none"
    elif sub_step == "complete":
        sub_step_label = "complete"
    else:
        sub_step_label = sub_step.replace("_", " ")
    return f"SPACER Chat | Phase: {phase} ({status}) | Sub-step: {sub_step_label}"


def _render_chat(cfg, transcript):
    clear()
    header = _render_header(cfg)
    click.echo(header)
    click.echo("=" * len(header))
    for role, text in transcript[-DISPLAY_MESSAGES:]:
        if role == "user":
            label = "You"
        elif role == "assistant":
            label = "SPACER"
        else:
            label = "System"
        click.echo(f"\n{label}:")
        click.echo(text.rstrip() if text else "")
    click.echo("")


def _save_conversation(transcript, cfg):
    notes_dir = Path("notes/ideation")
    notes_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = notes_dir / f"discussion-{stamp}.md"

    phase = get_phase(cfg)
    status = get_phase_status(cfg)
    sub_step = get_current_sub_step(cfg) or "none"
    sub_step = sub_step.replace("_", " ")

    lines = [
        "# SPACER Discussion",
        "",
        f"- Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"- Phase: {phase} ({status})",
        f"- Sub-step: {sub_step}",
        "",
        "## Transcript",
        "",
    ]

    for role, text in transcript:
        if role == "user":
            label = "You"
        elif role == "assistant":
            label = "SPACER"
        else:
            label = "System"
        lines.append(f"### {label}")
        lines.append((text or "").rstrip())
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def _search_inline(query, limit=5):
    r = _s2_get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": query, "limit": limit, "fields": _s2_fields()},
    )
    data = r.json().get("data", [])
    if not data:
        return f'No results found for "{query}".'

    lines = [f'Results for "{query}":']
    for idx, paper in enumerate(data, 1):
        authors = ", ".join(a.get("name", "") for a in paper.get("authors", [])[:3]) or "Unknown authors"
        if len(paper.get("authors", [])) > 3:
            authors += " et al."
        year = paper.get("year", "?")
        title = paper.get("title", "?")
        venue = paper.get("venue", "")
        lines.append(f"[{idx}] {title} ({year})")
        lines.append(f"    {authors}")
        if venue:
            lines.append(f"    {venue}")
    return "\n".join(lines)


def _review_drafts():
    files = []
    for pattern in ["constitution/*.md", "paper/sections/*", "paper/plan/*.md"]:
        files.extend(sorted(Path(".").glob(pattern)))

    files = [p for p in files if p.is_file() and p.name != ".gitkeep"]
    if not files:
        return "No draft files found yet."

    lines = ["Draft files:"]
    for path in files:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            preview = "(unreadable)"
        else:
            preview = "(empty)"
            for line in content.splitlines():
                if line.strip():
                    preview = line.strip()
                    break
            if len(preview) > 90:
                preview = preview[:87] + "..."
        lines.append(f"- {path}: {preview}")
    return "\n".join(lines)


def _command_help():
    return (
        "Slash commands:\n"
        "/status\n"
        "/phase\n"
        '/bib search "query"\n'
        "/supply <filepath>\n"
        "/constitute\n"
        "/review\n"
        "/save\n"
        "/next\n"
        "/quit or /exit"
    )


def _handle_slash_command(command_text, client, config_path, transcript, history):
    try:
        parts = shlex.split(command_text)
    except ValueError as exc:
        transcript.append(("system", f"Command parse error: {exc}"))
        return False, None

    if not parts:
        return False, None

    cmd = parts[0].lower()

    if cmd in {"/quit", "/exit"}:
        cfg = load_spacer_config(config_path)
        saved = _save_conversation(transcript, cfg)
        return True, f"Saved conversation to {saved}"

    if cmd == "/help":
        transcript.append(("system", _command_help()))
        return False, None

    if cmd == "/status":
        cfg = load_spacer_config(config_path)
        transcript.append(("system", format_status(cfg)))
        return False, None

    if cmd == "/phase":
        cfg = load_spacer_config(config_path)
        transcript.append(("system", format_phase_info(cfg)))
        return False, None

    if cmd == "/bib":
        if len(parts) >= 3 and parts[1].lower() == "search":
            query = " ".join(parts[2:])
            try:
                result = _search_inline(query)
            except Exception as exc:
                result = f"Bibliography search failed: {exc}"
            transcript.append(("system", result))
        else:
            transcript.append(("system", 'Usage: /bib search "query"'))
        return False, None

    if cmd == "/supply":
        if len(parts) < 2:
            transcript.append(("system", "Usage: /supply <filepath>"))
            return False, None

        supply_path = Path(parts[1]).expanduser()
        if not supply_path.is_absolute():
            supply_path = (Path.cwd() / supply_path).resolve()
        if not supply_path.exists() or not supply_path.is_file():
            transcript.append(("system", f"File not found: {supply_path}"))
            return False, None

        try:
            content = supply_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            transcript.append(("system", f"Failed to read file: {exc}"))
            return False, None

        trimmed = content[:MAX_SUPPLY_CHARS]
        note = ""
        if len(content) > MAX_SUPPLY_CHARS:
            note = f"\n\n[Truncated to first {MAX_SUPPLY_CHARS} characters.]"
        payload = (
            f"User supplied file: {supply_path}\n"
            "Treat the following content as trusted project context:\n\n"
            f"{trimmed}{note}"
        )
        history.append({"role": "user", "content": payload})
        _trim_history(history)
        transcript.append(("system", f"Added file context: {supply_path}"))
        return False, None

    if cmd == "/constitute":
        if client is None:
            transcript.append(("system", "No API key configured. Run `spacer auth` first."))
            return False, None

        prompt = (
            "Generate markdown for constitution/ideation.md based on this discussion. "
            "Include sections for McEnerney framing, terminology, scope, positioning, "
            "key papers and their roles, and explicit decisions. Return only markdown."
        )
        click.echo("SPACER is drafting constitution...")
        try:
            draft = _ask_model(client, config_path, history, prompt)
        except Exception as exc:
            transcript.append(("system", f"Constitution generation failed: {exc}"))
            return False, None

        constitution_path = Path("constitution/ideation.md")
        constitution_path.parent.mkdir(parents=True, exist_ok=True)
        constitution_path.write_text(draft, encoding="utf-8")
        transcript.append(("assistant", draft))
        transcript.append(("system", f"Saved constitution draft to {constitution_path}"))
        return False, None

    if cmd == "/review":
        transcript.append(("system", _review_drafts()))
        return False, None

    if cmd == "/save":
        cfg = load_spacer_config(config_path)
        saved = _save_conversation(transcript, cfg)
        transcript.append(("system", f"Saved conversation to {saved}"))
        return False, None

    if cmd == "/next":
        try:
            _, message, _ = advance_sub_step(config_path)
        except Exception as exc:
            message = f"Failed to advance sub-step: {exc}"
        transcript.append(("system", message))
        return False, None

    transcript.append(("system", f"Unknown command: {cmd}\n{_command_help()}"))
    return False, None


@click.command("chat")
@click.option("--config-path", default="spacer.yaml", show_default=True, help="Path to project config.")
def chat_cmd(config_path):
    """Launch SPACER interactive chat interface."""
    if not Path(config_path).exists():
        click.echo("No spacer.yaml found. Run `spacer init` first.", err=True)
        raise SystemExit(1)

    api_key = get_anthropic_api_key()
    client = Anthropic(api_key=api_key) if api_key else None

    transcript = [("system", "Interactive SPACER chat started. Type /help for commands.")]
    if not client:
        transcript.append(
            (
                "system",
                "Anthropic API key not found. Run `spacer auth` or set ANTHROPIC_API_KEY. "
                "Slash commands still work.",
            )
        )
    history = []

    session = PromptSession()
    while True:
        cfg = load_spacer_config(config_path)
        _render_chat(cfg, transcript)

        try:
            user_input = session.prompt("you> ").strip()
        except (KeyboardInterrupt, EOFError):
            saved = _save_conversation(transcript, cfg)
            click.echo(f"\nSaved conversation to {saved}")
            break

        if not user_input:
            continue

        transcript.append(("user", user_input))

        if user_input.startswith("/"):
            should_exit, message = _handle_slash_command(
                user_input, client, config_path, transcript, history
            )
            if should_exit:
                if message:
                    click.echo(message)
                break
            continue

        if client is None:
            transcript.append(("system", "No API key configured. Run `spacer auth` first."))
            continue

        click.echo("SPACER is thinking...")
        try:
            reply = _ask_model(client, config_path, history, user_input)
        except Exception as exc:
            transcript.append(("system", f"LLM request failed: {exc}"))
            continue

        transcript.append(("assistant", reply))
