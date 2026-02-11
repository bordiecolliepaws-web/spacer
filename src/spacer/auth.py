import json
import os
from pathlib import Path

import click
from anthropic import Anthropic

MODEL_NAME = "claude-sonnet-4-5"
AUTH_DIR = Path.home() / ".config" / "spacer"
AUTH_FILE = AUTH_DIR / "auth.json"


def get_anthropic_api_key():
    """Resolve Anthropic key from env first, then saved auth.json."""
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key

    if not AUTH_FILE.exists():
        return None

    try:
        with open(AUTH_FILE) as f:
            payload = json.load(f)
    except Exception:
        return None

    key = (payload.get("anthropic_api_key") or "").strip()
    return key or None


def save_anthropic_api_key(api_key):
    """Save Anthropic key with restrictive permissions."""
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(AUTH_DIR, 0o700)
    except OSError:
        pass

    tmp_path = AUTH_FILE.with_suffix(".json.tmp")
    payload = {"anthropic_api_key": api_key}
    with open(tmp_path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(AUTH_FILE)
    os.chmod(AUTH_FILE, 0o600)


def test_anthropic_connection(api_key):
    """Run a small Anthropic API request to validate the key."""
    client = Anthropic(api_key=api_key)
    client.messages.create(
        model=MODEL_NAME,
        max_tokens=8,
        messages=[{"role": "user", "content": "Reply with OK."}],
    )


@click.command("auth")
@click.option(
    "--key",
    "api_key_opt",
    default=None,
    help="Anthropic API key (defaults to ANTHROPIC_API_KEY env or interactive prompt).",
)
def auth_cmd(api_key_opt):
    """Authenticate and store Anthropic API credentials."""
    api_key = (api_key_opt or "").strip()
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        api_key = click.prompt("Anthropic API key", hide_input=True).strip()
    if not api_key:
        click.echo("No API key provided.", err=True)
        raise SystemExit(1)

    click.echo("Testing Anthropic connection...")
    try:
        test_anthropic_connection(api_key)
    except Exception as exc:
        click.echo(f"Anthropic authentication failed: {exc}", err=True)
        raise SystemExit(1)

    save_anthropic_api_key(api_key)
    click.echo(f"Saved credentials to {AUTH_FILE}")
    click.echo("Authentication successful.")
