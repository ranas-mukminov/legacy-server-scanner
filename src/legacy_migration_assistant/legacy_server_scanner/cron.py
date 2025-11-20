"""Cron parsing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from legacy_migration_assistant.core.models import CronJob
from legacy_migration_assistant.core.utils import run_command, safe_read_file


def parse_crontab_text(content: str, source: str, user: Optional[str] = None) -> List[CronJob]:
    """Parse crontab content into CronJob records."""

    jobs: List[CronJob] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped.split()[0]:
            # Environment variable assignment, skip
            continue
        parts = stripped.split(None, 5)
        if len(parts) < 6:
            continue
        schedule = " ".join(parts[0:5])
        command = parts[5]
        jobs.append(CronJob(schedule=schedule, command=command, user=user, source=source))
    return jobs


def collect_cron() -> List[CronJob]:
    """Collect cron jobs from user and system crontabs."""

    jobs: List[CronJob] = []

    code, stdout, _ = run_command(["crontab", "-l"])
    if code == 0 and stdout:
        jobs.extend(parse_crontab_text(stdout, source="user"))

    system_cron = safe_read_file("/etc/crontab")
    if system_cron:
        jobs.extend(parse_crontab_text(system_cron, source="/etc/crontab", user="root"))

    for path in Path("/etc").glob("cron.*/*"):
        if path.is_file():
            content = safe_read_file(str(path))
            if content:
                jobs.extend(parse_crontab_text(content, source=str(path), user="root"))

    return jobs
