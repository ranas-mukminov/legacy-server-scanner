"""Utility helpers for the legacy migration assistant."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional


def run_command(command: Iterable[str], timeout: int = 10) -> tuple[int, str, str]:
    """Run a shell command safely and return (exit_code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        return 1, "", f"{exc}"


def safe_read_file(path: str) -> Optional[str]:
    """Return file content or None if missing/unreadable."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def detect_systemd() -> bool:
    """Best-effort systemd detection."""
    return os.path.isdir("/run/systemd/system")
