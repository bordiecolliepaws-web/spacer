"""SPACER auth — configure LLM backend (coding agent CLI)."""

import json
import os
import shutil
from pathlib import Path

import click

AUTH_DIR = Path.home() / ".config" / "spacer"
AUTH_FILE = AUTH_DIR / "auth.json"


def detect_coding_agents():
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
    return get_config().get("backend")


def get_api_key():
    """Get API key if configured (for future direct API mode)."""
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key
    return get_config().get("api_key", "")


@click.command("auth")
def auth_cmd():
    """Configure SPACER's LLM backend."""
    config = get_config()

    click.echo("═══ SPACER Auth Setup ═══\n")
    click.echo("SPACER uses your existing coding agent CLI (claude or codex)")
    click.echo("with your subscription — no API key needed.\n")

    agents = detect_coding_agents()
    if not agents:
        click.echo("No coding agent CLIs found!")
        click.echo("Install one:")
        click.echo("  Claude Code: npm install -g @anthropic-ai/claude-code")
        click.echo("  Codex CLI:   npm install -g @openai/codex")
        raise SystemExit(1)

    for i, (name, desc) in enumerate(agents, 1):
        click.echo(f"  {i}. {desc}")
    click.echo()

    if len(agents) == 1:
        choice = 1
        click.echo(f"Using: {agents[0][1]}")
    else:
        choice = click.prompt("Choose backend", type=int, default=1)

    if choice < 1 or choice > len(agents):
        click.echo("Invalid choice.", err=True)
        raise SystemExit(1)

    backend = agents[choice - 1][0]
    config["backend"] = backend
    save_config(config)

    click.echo(f"\n✓ SPACER configured with {backend}")
    click.echo(f"  Config: {AUTH_FILE}")
    click.echo(f"\n  Run `spacer chat` to start!")
