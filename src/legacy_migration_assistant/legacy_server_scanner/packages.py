"""Package discovery for Debian/RHEL families."""

from __future__ import annotations

from typing import List, Optional

from legacy_migration_assistant.core.models import OSFamily, Package
from legacy_migration_assistant.core.utils import run_command
from legacy_migration_assistant.legacy_server_scanner.os_detection import detect_os_family


def parse_dpkg_output(output: str) -> List[Package]:
    """Parse `dpkg -l` or `apt list --installed` style output."""
    packages: List[Package] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Listing...") or line.startswith("Desired") or line.startswith("||"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        status, name, version = parts[0], parts[1], parts[2]
        if status.startswith("ii") or status.startswith("install") or status.startswith("rc"):
            packages.append(Package(name=name, version=version, source="dpkg"))
    return packages


def parse_rpm_output(output: str) -> List[Package]:
    """Parse `rpm -qa` or `dnf list installed` style output."""

    packages: List[Package] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Installed Packages"):
            continue
        if " " in line:
            line = line.split()[0]
        base = line.rsplit(".", 1)[0]
        parts = base.split("-")
        if len(parts) >= 2:
            name = "-".join(parts[:-2]) or parts[0]
            version = "-".join(parts[-2:])
            packages.append(Package(name=name, version=version, source="rpm"))
    return packages


def collect_packages(os_family: Optional[OSFamily] = None) -> List[Package]:
    """Collect packages for the current system using appropriate tooling."""

    family = os_family or detect_os_family()
    if family == OSFamily.DEBIAN:
        code, stdout, _ = run_command(["dpkg", "-l"])
        if code == 0:
            return parse_dpkg_output(stdout)
        code, stdout, _ = run_command(["apt", "list", "--installed"])
        return parse_dpkg_output(stdout) if code == 0 else []

    if family == OSFamily.RHEL:
        code, stdout, _ = run_command(["rpm", "-qa"])
        if code == 0:
            return parse_rpm_output(stdout)
        code, stdout, _ = run_command(["dnf", "list", "installed"])
        return parse_rpm_output(stdout) if code == 0 else []

    return []
