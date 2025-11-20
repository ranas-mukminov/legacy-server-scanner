"""Discovery of common configuration files without reading secrets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from legacy_migration_assistant.core.models import ConfigFile
from legacy_migration_assistant.core.utils import safe_read_file

KNOWN_PATHS = [
    ("nginx", ["/etc/nginx/nginx.conf", "/etc/nginx/conf.d", "/etc/nginx/sites-enabled"]),
    ("apache", ["/etc/httpd", "/etc/apache2"]),
    ("php-fpm", ["/etc/php-fpm.d", "/etc/php", "/etc/php/*/fpm"]),
    ("mysql", ["/etc/mysql/my.cnf", "/var/lib/mysql"]),
    ("postgresql", ["/etc/postgresql", "/var/lib/postgresql"]),
    ("redis", ["/etc/redis/redis.conf"]),
    ("rabbitmq", ["/etc/rabbitmq/rabbitmq.conf", "/etc/rabbitmq/conf.d"]),
]


def _extract_ports(content: str) -> List[int]:
    ports: List[int] = []
    for match in re.finditer(r"listen\s+([^;\s]+)", content):
        raw = match.group(1)
        if ":" in raw:
            raw = raw.split(":")[-1]
        try:
            ports.append(int(raw))
        except ValueError:
            continue
    return sorted({p for p in ports if p > 0})


def _scan_path(service: str, path: str) -> List[ConfigFile]:
    results: List[ConfigFile] = []
    for resolved in Path().glob(path):
        if resolved.is_file():
            content = safe_read_file(str(resolved)) or ""
            metadata: Dict[str, object] = {}
            ports = _extract_ports(content)
            if ports:
                metadata["ports"] = ports
            results.append(ConfigFile(path=str(resolved), service=service, metadata=metadata))
    return results


def discover_configs() -> List[ConfigFile]:
    """Discover known config files with minimal metadata extraction."""

    configs: List[ConfigFile] = []
    for service, paths in KNOWN_PATHS:
        for path in paths:
            configs.extend(_scan_path(service, path))
    return configs
