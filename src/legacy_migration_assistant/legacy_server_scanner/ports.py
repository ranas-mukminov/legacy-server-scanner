"""Network port discovery using ss/netstat."""

from __future__ import annotations

import re
from typing import List

from legacy_migration_assistant.core.models import Port
from legacy_migration_assistant.core.utils import run_command


_USERS_RE = re.compile(r"users:\\(\\((?P<info>[^)]*)\\)\\)")


def _extract_process(segment: str) -> str:
    match = _USERS_RE.search(segment)
    if match:
        return match.group("info")
    return ""


def parse_ss_output(output: str) -> List[Port]:
    ports: List[Port] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("netid"):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        proto = parts[0]
        local = parts[4]
        proc_segment = " ".join(parts[5:]) if len(parts) > 5 else ""
        process = _extract_process(proc_segment) or None
        address, _, port_str = local.rpartition(":")
        try:
            port_num = int(port_str)
        except ValueError:
            continue
        ports.append(Port(protocol=proto, address=address or "*", port=port_num, process=process))
    return ports


def parse_netstat_output(output: str) -> List[Port]:
    ports: List[Port] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Proto") or line.startswith("Active"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        proto = parts[0]
        local = parts[3]
        address, _, port_str = local.rpartition(":")
        try:
            port_num = int(port_str)
        except ValueError:
            continue
        ports.append(Port(protocol=proto, address=address or "*", port=port_num, process=None))
    return ports


def collect_ports() -> List[Port]:
    """Collect listening ports."""

    code, stdout, _ = run_command(["ss", "-tulpen"])
    if code == 0 and stdout:
        parsed = parse_ss_output(stdout)
        if parsed:
            return parsed
    code, stdout, _ = run_command(["netstat", "-tulpen"])
    return parse_netstat_output(stdout) if code == 0 else []

