"""SPACER LLM layer — brain (API) + hands (coding agent CLI)."""

import subprocess
import tempfile
from pathlib import Path

from .auth import get_api_key, get_backend, get_brain_model


# ─── Brain: direct API for discussion/evaluation/planning ───

def brain(system_prompt: str, messages: list, stream: bool = False):
    """Call SPACER's brain (Anthropic API) for interactive tasks.
    
    Args:
        system_prompt: System instructions
        messages: List of {"role": "user"|"assistant", "content": "..."}
        stream: Whether to stream the response
    
    Returns:
        Response text (or generator if streaming)
    """
    from anthropic import Anthropic

    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("No API key configured. Run `spacer auth` first.")

    model = get_brain_model()
    client = Anthropic(api_key=api_key)

    if stream:
        return _brain_stream(client, model, system_prompt, messages)

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
    )

    # Extract text
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts).strip() or "(No response)"


def _brain_stream(client, model, system_prompt, messages):
    """Stream brain response, yielding text chunks."""
    with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


# ─── Hands: coding agent CLI for execution tasks ───

def hands(prompt: str, workdir: str = ".", backend: str = None, timeout: int = 300):
    """Launch coding agent to execute a task in the repo.
    
    Args:
        prompt: Task description for the coding agent
        workdir: Working directory for the agent
        backend: "claude" or "codex" (auto-detects if None)
        timeout: Max seconds to wait
    
    Returns:
        (stdout, stderr, returncode)
    """
    if backend is None:
        backend = get_backend()
    if not backend:
        raise RuntimeError("No coding agent configured. Run `spacer auth` first.")

    if backend == "claude":
        return _hands_claude(prompt, workdir, timeout)
    elif backend == "codex":
        return _hands_codex(prompt, workdir, timeout)
    else:
        raise RuntimeError(f"Unknown backend: {backend}")


def _hands_claude(prompt: str, workdir: str, timeout: int):
    """Execute task via Claude Code CLI."""
    try:
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workdir,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timed out", -1
    except FileNotFoundError:
        return "", "claude CLI not found", -1


def _hands_codex(prompt: str, workdir: str, timeout: int):
    """Execute task via Codex CLI."""
    try:
        result = subprocess.run(
            ["codex", "exec", "--full-auto", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workdir,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timed out", -1
    except FileNotFoundError:
        return "", "codex CLI not found", -1


def hands_background(prompt: str, workdir: str = ".", backend: str = None):
    """Launch coding agent in background, return process handle.
    
    For long-running tasks (experiments, large drafts).
    """
    if backend is None:
        backend = get_backend()

    if backend == "claude":
        cmd = ["claude", "--print", prompt]
    elif backend == "codex":
        cmd = ["codex", "exec", "--full-auto", prompt]
    else:
        raise RuntimeError(f"Unknown backend: {backend}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=workdir,
    )
    return proc
