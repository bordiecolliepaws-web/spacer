"""SPACER LLM layer — brain + hands, both via coding agent CLI for now."""

import subprocess
import tempfile
import json
from pathlib import Path

from .auth import get_backend


# ─── Brain: for discussion, evaluation, planning ───

def brain(system_prompt: str, messages: list, stream: bool = False):
    """Call SPACER's brain for interactive tasks.
    
    Uses claude --print or codex exec under the hood.
    
    Args:
        system_prompt: System instructions
        messages: List of {"role": "user"|"assistant", "content": "..."}
    
    Returns:
        Response text
    """
    backend = get_backend()
    if not backend:
        raise RuntimeError("No backend configured. Run `spacer auth` first.")

    # Build a single prompt from system + message history
    prompt_parts = [f"<system>\n{system_prompt}\n</system>\n"]
    for msg in messages:
        role = msg["role"].capitalize()
        prompt_parts.append(f"<{role}>\n{msg['content']}\n</{role}>")
    
    # Ask for assistant response
    prompt_parts.append("<Assistant>")
    full_prompt = "\n".join(prompt_parts)

    if backend == "claude":
        return _brain_claude(system_prompt, messages)
    elif backend == "codex":
        return _brain_codex(full_prompt)
    else:
        raise RuntimeError(f"Unknown backend: {backend}")


def _brain_claude(system_prompt: str, messages: list):
    """Use claude --print with proper system prompt and conversation."""
    # Claude Code CLI supports --system-prompt from a file
    # and reads the user message as the argument
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(system_prompt)
        sys_file = f.name

    try:
        # Build conversation as a single prompt for --print mode
        parts = []
        for msg in messages:
            if msg["role"] == "user":
                parts.append(f"User: {msg['content']}")
            else:
                parts.append(f"Assistant: {msg['content']}")
        conversation = "\n\n".join(parts)

        result = subprocess.run(
            ["claude", "--print", "--system-prompt", sys_file, conversation],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout.strip() or result.stderr.strip() or "(No response)"
    except subprocess.TimeoutExpired:
        return "(Response timed out)"
    except FileNotFoundError:
        return "(claude CLI not found)"
    finally:
        Path(sys_file).unlink(missing_ok=True)


def _brain_codex(full_prompt: str):
    """Use codex exec for brain calls."""
    try:
        result = subprocess.run(
            ["codex", "exec", full_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout.strip() or result.stderr.strip() or "(No response)"
    except subprocess.TimeoutExpired:
        return "(Response timed out)"
    except FileNotFoundError:
        return "(codex CLI not found)"


# ─── Hands: coding agent CLI for execution tasks ───

def hands(prompt: str, workdir: str = ".", backend: str = None, timeout: int = 300):
    """Launch coding agent to execute a task in the repo.
    
    Args:
        prompt: Task description for the coding agent
        workdir: Working directory
        timeout: Max seconds
    
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
    """Launch coding agent in background, return process handle."""
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
