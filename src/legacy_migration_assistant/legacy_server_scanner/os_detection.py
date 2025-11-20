"""OS detection helpers."""

from __future__ import annotations

import re
from typing import Dict, Optional

from legacy_migration_assistant.core.models import OSFamily, OSRelease
from legacy_migration_assistant.core.utils import safe_read_file


def _parse_os_release(content: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in content.splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"')
        data[key.strip()] = value
    return data


def detect_os_release(raw: Optional[str] = None) -> Optional[OSRelease]:
    """Parse /etc/os-release (or provided text) into OSRelease."""

    content = raw if raw is not None else safe_read_file("/etc/os-release")
    if not content:
        return None
    data = _parse_os_release(content)
    os_id = data.get("ID", "unknown")
    version = data.get("VERSION_ID", data.get("VERSION", ""))
    pretty = data.get("PRETTY_NAME", None)
    return OSRelease(id=os_id, version_id=version, pretty_name=pretty)


def detect_os_family(raw: Optional[str] = None) -> OSFamily:
    """Detect OS family from os-release data."""

    release = detect_os_release(raw)
    if not release:
        return OSFamily.OTHER

    os_id = release.id.lower()
    if re.search(r"(debian|ubuntu|mint)", os_id):
        return OSFamily.DEBIAN
    if re.search(r"(rhel|centos|alma|rocky|fedora|ol)", os_id):
        return OSFamily.RHEL

    return OSFamily.OTHER
