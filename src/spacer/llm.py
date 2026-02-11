"""SPACER LLM backend — shells out to claude or codex CLI."""

import subprocess
import tempfile
from pathlib import Path

from .auth import get_backend


def call_llm(system_prompt: str, user_message: str, backend: str = None) -> str:
    """Call the LLM via CLI backend.
    
    Args:
        system_prompt: System instructions for the LLM
        user_message: The user's message/prompt
        backend: "claude" or "codex" (auto-detects if None)
    
    Returns:
        The LLM's response text
    """
    if backend is None:
        backend = get_backend()
    if not backend:
        raise RuntimeError("No backend configured. Run `spacer auth` first.")

    if backend == "claude":
        return _call_claude(system_prompt, user_message)
    elif backend == "codex":
        return _call_codex(system_prompt, user_message)
    else:
        raise RuntimeError(f"Unknown backend: {backend}")


def _call_claude(system_prompt: str, user_message: str) -> str:
    """Call Claude Code CLI."""
    # Write system prompt to temp file for --system-prompt flag
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(system_prompt)
        system_file = f.name

    try:
        # claude --print outputs response to stdout without interactive mode
        # --system-prompt reads from file
        full_prompt = user_message
        result = subprocess.run(
            ["claude", "--print", "--system-prompt", system_file, full_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            # Try simpler invocation
            result = subprocess.run(
                ["claude", "--print", full_prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
        return result.stdout.strip() or result.stderr.strip() or "(No response)"
    except subprocess.TimeoutExpired:
        return "(Response timed out)"
    except FileNotFoundError:
        return "(claude CLI not found. Install: npm install -g @anthropic-ai/claude-code)"
    finally:
        Path(system_file).unlink(missing_ok=True)


def _call_codex(system_prompt: str, user_message: str) -> str:
    """Call Codex CLI."""
    # codex exec runs a one-shot prompt
    # Combine system + user into one prompt since codex exec doesn't have --system-prompt
    combined = f"{system_prompt}\n\n---\n\nUser request:\n{user_message}"

    try:
        result = subprocess.run(
            ["codex", "exec", combined],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout.strip() or result.stderr.strip() or "(No response)"
    except subprocess.TimeoutExpired:
        return "(Response timed out)"
    except FileNotFoundError:
        return "(codex CLI not found. Install: npm install -g @openai/codex)"


def call_llm_streaming(system_prompt: str, user_message: str, backend: str = None):
    """Call LLM and yield chunks as they arrive (for TUI streaming).
    
    Falls back to non-streaming if streaming not available.
    """
    # For now, just call and return full response
    # TODO: implement actual streaming with subprocess pipes
    response = call_llm(system_prompt, user_message, backend)
    yield response
