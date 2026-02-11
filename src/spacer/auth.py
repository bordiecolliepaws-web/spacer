"""SPACER auth — configure brain (API) and hands (coding agent CLI)."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import click

AUTH_DIR = Path.home() / ".config" / "spacer"
AUTH_FILE = AUTH_DIR / "auth.json"


def detect_coding_agents():
    """Detect available coding agent CLIs."""
    agents = []
    if shutil.which("claude"):
        agents.append(("claude", "Claude Code CLI (Anthropic subscription)"))
    if shutil.which("codex"):
        agents.append(("codex", "Codex CLI (ChatGPT subscription)"))
    return agents


def get_config():
    if not AUTH_FILE.exists():
        return {}
    try:
        with open(AUTH_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config):
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(AUTH_DIR, 0o700)
    except OSError:
        pass
    tmp = AUTH_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    os.chmod(tmp, 0o600)
    tmp.replace(AUTH_FILE)


def get_backend():
    """Get configured coding agent backend."""
    return get_config().get("coding_agent")


def get_api_key():
    """Get API key for SPACER's brain. Checks env, then config."""
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key
    return get_config().get("api_key", "")


def get_brain_model():
    """Get model for SPACER's brain."""
    return get_config().get("brain_model", "claude-sonnet-4-5")


@click.command("auth")
def auth_cmd():
    """Configure SPACER: brain (API) + hands (coding agent)."""
    config = get_config()

    click.echo("═══ SPACER Auth Setup ═══\n")

    # --- Brain (API connection) ---
    click.echo("1. BRAIN — SPACER's own LLM connection")
    click.echo("   (for discussion, evaluation, planning)\n")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        click.echo(f"   Found ANTHROPIC_API_KEY in environment ✓")
    else:
        api_key = config.get("api_key", "")
        if api_key:
            click.echo(f"   Found saved API key ✓")
        else:
            api_key = click.prompt("   Anthropic API key", hide_input=True).strip()

    if api_key:
        click.echo("   Testing connection...")
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8,
                messages=[{"role": "user", "content": "OK"}],
            )
            click.echo("   ✓ Brain connected.\n")
            config["api_key"] = api_key
        except Exception as e:
            click.echo(f"   ⚠ Connection failed: {e}")
            click.echo("   Saving key anyway — you can fix later.\n")
            config["api_key"] = api_key
    else:
        click.echo("   ⚠ No API key. Brain won't work without it.\n")

    # --- Hands (coding agent) ---
    click.echo("2. HANDS — Coding agent for execution tasks")
    click.echo("   (for writing code, drafting LaTeX, running experiments)\n")

    agents = detect_coding_agents()
    if not agents:
        click.echo("   No coding agent CLIs found.")
        click.echo("   Install one of:")
        click.echo("     Claude Code: npm install -g @anthropic-ai/claude-code")
        click.echo("     Codex CLI:   npm install -g @openai/codex")
        click.echo("   (You can set this up later)\n")
    else:
        for i, (name, desc) in enumerate(agents, 1):
            click.echo(f"   {i}. {desc}")
        click.echo()

        if len(agents) == 1:
            choice = 1
        else:
            choice = click.prompt("   Choose coding agent", type=int, default=1)

        if 1 <= choice <= len(agents):
            agent_name = agents[choice - 1][0]
            config["coding_agent"] = agent_name
            click.echo(f"   ✓ Using {agent_name} for execution.\n")

    # --- Model selection ---
    click.echo("3. BRAIN MODEL")
    model = click.prompt(
        "   Model for SPACER's brain",
        default=config.get("brain_model", "claude-sonnet-4-5"),
    )
    config["brain_model"] = model

    save_config(config)
    click.echo(f"\n✓ Config saved to {AUTH_FILE}")
    click.echo(f"  Brain: {config.get('brain_model', '?')} via Anthropic API")
    click.echo(f"  Hands: {config.get('coding_agent', 'not configured')}")
