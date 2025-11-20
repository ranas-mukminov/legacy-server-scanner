"""
Service inspection logic for systemd and init-like systems.
"""

from __future__ import annotations

import os
from typing import List

from legacy_migration_assistant.core.models import Service
from legacy_migration_assistant.core.utils import detect_systemd, run_command


def parse_systemctl_list_units(output: str) -> List[Service]:
    services: List[Service] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("UNIT") or line.startswith("--"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        unit = parts[0]
        active = parts[2]
        sub = parts[3]
        name = unit.replace(".service", "")
        status = f"{active}/{sub}" if sub else active
        services.append(Service(name=name, status=status, main_cmd=None, manager="systemd"))
    return services


def parse_ps_aux(output: str) -> List[Service]:
    services: List[Service] = []
    for line in output.splitlines():
        if line.startswith("USER"):
            continue
        parts = line.split(None, 10)
        if len(parts) < 11:
            continue
        pid = None
        try:
            pid = int(parts[1])
        except (ValueError, IndexError):
            pid = None
        cmd = parts[10]
        name = os.path.basename(cmd.split()[0]) if cmd else "process"
        services.append(Service(name=name, status="running", main_cmd=cmd, manager="ps", pid=pid))
    return services


def collect_services() -> List[Service]:
    """Collect running services using systemd or ps fallback."""

    if detect_systemd():
        code, stdout, _ = run_command(["systemctl", "list-units", "--type=service", "--state=running"])
        if code == 0:
            parsed = parse_systemctl_list_units(stdout)
            if parsed:
                return parsed

    code, stdout, _ = run_command(["ps", "aux"])
    return parse_ps_aux(stdout) if code == 0 else []
