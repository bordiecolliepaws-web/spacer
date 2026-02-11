"""SPACER auth — detect and configure LLM backend."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import click

AUTH_DIR = Path.home() / ".config" / "spacer"
AUTH_FILE = AUTH_DIR / "auth.json"


def detect_backends():
    """Detect available coding agent CLIs."""
    backends = []
    if shutil.which("claude"):
        backends.append(("claude", "Claude Code CLI (Anthropic subscription)"))
    if shutil.which("codex"):
        backends.append(("codex", "Codex CLI (ChatGPT subscription)"))
    return backends


def get_config():
    """Load saved config."""
    if not AUTH_FILE.exists():
        return {}
    try:
        with open(AUTH_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config):
    """Save config with restrictive permissions."""
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
    """Get configured backend name."""
    config = get_config()
    return config.get("backend")


def test_backend(backend):
    """Quick test that the backend CLI works."""
    try:
        if backend == "claude":
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        elif backend == "codex":
            result = subprocess.run(
                ["codex", "--version"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
    except Exception:
        return False
    return False


@click.command("auth")
def auth_cmd():
    """Configure LLM backend for SPACER."""
    backends = detect_backends()

    if not backends:
        click.echo("No coding agent CLIs found!")
        click.echo("Install one of:")
        click.echo("  Claude Code: npm install -g @anthropic-ai/claude-code")
        click.echo("  Codex CLI:   npm install -g @openai/codex")
        raise SystemExit(1)

    click.echo("Available backends:\n")
    for i, (name, desc) in enumerate(backends, 1):
        click.echo(f"  {i}. {desc}")

    click.echo()

    if len(backends) == 1:
        choice = 1
        click.echo(f"Only one backend found, using: {backends[0][1]}")
    else:
        choice = click.prompt("Choose backend", type=int, default=1)

    if choice < 1 or choice > len(backends):
        click.echo("Invalid choice.", err=True)
        raise SystemExit(1)

    backend_name = backends[choice - 1][0]

    click.echo(f"\nTesting {backend_name}...")
    if test_backend(backend_name):
        click.echo("✓ Backend working.")
    else:
        click.echo("⚠ Could not verify backend, saving anyway.")

    config = get_config()
    config["backend"] = backend_name
    save_config(config)
    click.echo(f"\nSaved: using {backend_name} as LLM backend.")
    click.echo(f"Config: {AUTH_FILE}")
