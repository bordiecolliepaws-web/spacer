import os
import json
import stat
import click

AUTH_DIR = os.path.expanduser("~/.config/spacer")
AUTH_FILE = os.path.join(AUTH_DIR, "auth.json")


def get_api_key():
    """Get Anthropic API key from env, auth file, or openclaw auth-profiles."""
    # 1. Environment
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    # 2. Auth file
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE) as f:
            data = json.load(f)
        key = data.get("anthropic_api_key")
        if key:
            return key
    # 3. OpenClaw auth-profiles
    profiles_path = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    if os.path.exists(profiles_path):
        with open(profiles_path) as f:
            data = json.load(f)
        profile = data.get("profiles", {}).get("anthropic:default", {})
        key = profile.get("token")
        if key:
            return key
    return None


def save_api_key(key):
    os.makedirs(AUTH_DIR, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump({"anthropic_api_key": key}, f, indent=2)
    os.chmod(AUTH_FILE, stat.S_IRUSR | stat.S_IWUSR)


@click.command()
def auth_cmd():
    """Configure API authentication."""
    existing = get_api_key()
    if existing:
        click.echo(f"API key found: {existing[:12]}...")
        if not click.confirm("Replace it?", default=False):
            # Test connection
            _test_connection(existing)
            return

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        key = click.prompt("Anthropic API key", hide_input=True)

    _test_connection(key)
    save_api_key(key)
    click.echo(f"Saved to {AUTH_FILE}")


def _test_connection(key):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=32,
            messages=[{"role": "user", "content": "Say 'ok' and nothing else."}],
        )
        click.echo(f"✓ Connection successful (model: claude-sonnet-4-5)")
    except Exception as e:
        click.echo(f"✗ Connection failed: {e}")
