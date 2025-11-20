"""Discovery of common configuration files without reading secrets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from legacy_migration_assistant.core.models import ConfigFile
from legacy_migration_assistant.core.utils import safe_read_file


KNOWN_PATHS = [
    (\"nginx\", [\"/etc/nginx/nginx.conf\", \"/etc/nginx/conf.d\", \"/etc/nginx/sites-enabled\"]),
    (\"apache\", [\"/etc/httpd\", \"/etc/apache2\"]),
    (\"php-fpm\", [\"/etc/php-fpm.d\", \"/etc/php\", \"/etc/php/*/fpm\"]),
    (\"mysql\", [\"/etc/mysql/my.cnf\", \"/var/lib/mysql\"]),
    (\"postgresql\", [\"/etc/postgresql\", \"/var/lib/postgresql\"]),
    (\"redis\", [\"/etc/redis/redis.conf\"]),
    (\"rabbitmq\", [\"/etc/rabbitmq/rabbitmq.conf\", \"/etc/rabbitmq/conf.d\"]),
]


def _extract_ports(content: str) -> List[int]:
    ports: List[int] = []
    for match in re.finditer(r\"listen\\s+([^;\\s]+)\", content):
        raw = match.group(1)
        if \":\" in raw:\n+            raw = raw.split(\":\")[-1]\n+        try:\n+            ports.append(int(raw))\n+        except ValueError:\n+            continue\n+    return list(sorted({p for p in ports if p > 0}))\n+\n+\n+def _scan_path(service: str, path: str) -> List[ConfigFile]:\n+    results: List[ConfigFile] = []\n+    for resolved in Path().glob(path):\n+        if resolved.is_file():\n+            content = safe_read_file(str(resolved)) or \"\"\n+            metadata: Dict[str, object] = {}\n+            ports = _extract_ports(content)\n+            if ports:\n+                metadata[\"ports\"] = ports\n+            results.append(ConfigFile(path=str(resolved), service=service, metadata=metadata))\n+    return results\n+\n+\n+def discover_configs() -> List[ConfigFile]:\n+    \"\"\"Discover known config files with minimal metadata extraction.\"\"\"\n+\n+    configs: List[ConfigFile] = []\n+    for service, paths in KNOWN_PATHS:\n+        for path in paths:\n+            configs.extend(_scan_path(service, path))\n+    return configs\n+\n*** End Patch
