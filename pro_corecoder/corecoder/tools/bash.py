"""Shell command execution with safety checks.

Claude Code's BashTool is 1,143 lines. This is the distilled version:
- Output capture with truncation (head+tail preserved)
- Timeout support
- Dangerous command detection
- Working directory tracking (cd awareness)
"""

import os
import re
import subprocess
import tkinter as tk
from tkinter import messagebox
from .base import Tool

# track cwd across commands (Claude Code does this too)
_cwd: str | None = None

# patterns that could wreck the filesystem or leak secrets
_DANGEROUS_PATTERNS = [
    (r"\brm\s+(-\w*)?-r\w*\s+(/|~|\$HOME)", "recursive delete on home/root"),
    (r"\brm\s+(-\w*)?-rf\s", "force recursive delete"),
    (r"\bmkfs\b", "format filesystem"),
    (r"\bdd\s+.*of=/dev/", "raw disk write"),
    (r">\s*/dev/sd[a-z]", "overwrite block device"),
    (r"\bchmod\s+(-R\s+)?777\s+/", "chmod 777 on root"),
    (r":\(\)\s*\{.*:\|:.*\}", "fork bomb"),
    (r"\bcurl\b.*\|\s*(sudo\s+)?bash", "pipe curl to bash"),
    (r"\bwget\b.*\|\s*(sudo\s+)?bash", "pipe wget to bash"),
]


class BashTool(Tool):
    name = "bash"
    description = (
        "Execute a shell command. Returns stdout, stderr, and exit code. "
        "Use this for running tests, installing packages, git operations, etc. "
        "Note: STRICTLY FORBIDDEN to use this tool for data calculation or "
        "manipulating CSV/Excel files. Use data_analysis tool for that."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to run",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default 120)",
            },
        },
        "required": ["command"],
    }

    def execute(self, command: str, timeout: int = 120) -> str:
        global _cwd
        # safety check against strictly forbidden patterns
        warning = _check_dangerous(command)
        if warning:
            return f"⚠ Blocked: {warning}\nCommand: {command}\nIf intentional, modify the command to be more specific."

        # ==========================================
        # Human-in-the-loop (HITL) Deletion Interception (Upgraded)
        # ==========================================
        # Match common deletion commands AND Python/PowerShell bypass methods
        deletion_patterns = [
            r"\brm\b", r"\bdel\b", r"\berase\b", r"\brmdir\b", r"Remove-Item",
            r"\bunlink\b", r"os\.remove", r"os\.unlink", r"shutil\.rmtree", r"pathlib\.Path.*\.unlink"
        ]
        is_deletion = any(re.search(pattern, command, re.IGNORECASE) for pattern in deletion_patterns)

        if is_deletion:
            # Trigger native OS popup for manual review
            root = tk.Tk()
            root.wm_attributes("-topmost", 1)
            root.withdraw()

            is_approved = messagebox.askyesno(
                title="⚠️ CoreCoder Security Review",
                message=f"Agent is attempting to execute a potentially destructive command:\n\n{command}\n\nAllow execution?"
            )
            root.destroy()

            if not is_approved:
                # 终极防御：用 Prompt 强行打断 Agent 的继续尝试意图
                return (
                    f"Error: The human user explicitly DENIED the execution of '{command}'. "
                    "CRITICAL INSTRUCTION: You MUST respect this human decision. "
                    "DO NOT try to bypass this restriction using other commands, python scripts, or any other tools. "
                    "Stop the deletion process immediately and explicitly inform the user that the action was canceled."
                )
        # ==========================================
        # use tracked working directory
        cwd = _cwd or os.getcwd()

        # force utf-8 encoding for subprocess
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                encoding='utf-8',
                errors='replace',
                env=env
            )

            # track cd commands so next command runs in the right place
            if proc.returncode == 0:
                _update_cwd(command, cwd)
            out = proc.stdout
            if proc.stderr:
                out += f"\n[stderr]\n{proc.stderr}"
            if proc.returncode != 0:
                out += f"\n[exit code: {proc.returncode}]"

            # keep head + tail to preserve the most useful info
            if len(out) > 15_000:
                out = (
                    out[:6000]
                    + f"\n\n... truncated ({len(out)} chars total) ...\n\n"
                    + out[-3000:]
                )
            return out.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: timed out after {timeout}s"
        except Exception as e:
            return f"Error running command: {e}"


def _check_dangerous(cmd: str) -> str | None:
    """Return a warning string if the command looks destructive, else None."""
    for pattern, reason in _DANGEROUS_PATTERNS:
        if re.search(pattern, cmd):
            return reason
    return None


def _update_cwd(command: str, current_cwd: str):
    """Track directory changes from cd commands."""
    global _cwd
    # simple heuristic: look for cd at the end of a && chain or standalone
    parts = command.split("&&")
    for part in parts:
        part = part.strip()
        if part.startswith("cd "):
            target = part[3:].strip().strip("'\"")
            if target:
                new_dir = os.path.normpath(os.path.join(current_cwd, os.path.expanduser(target)))
                if os.path.isdir(new_dir):
                    _cwd = new_dir