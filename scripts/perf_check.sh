#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import json
from pathlib import Path
from legacy_migration_assistant.legacy_server_scanner.topology_builder import build_topology
from legacy_migration_assistant.legacy_server_scanner.compose_generator import build_compose
from legacy_migration_assistant.legacy_server_scanner.exporter import export_topology
from legacy_migration_assistant.core.models import Package, Service, Port, CronJob, ConfigFile

packages = [Package(name=f"pkg{i}", version="1.0") for i in range(200)]
services = [Service(name=f"svc{i}", status="running") for i in range(50)]
ports = [Port(protocol="tcp", address="0.0.0.0", port=8000 + i) for i in range(10)]
cron = [CronJob(schedule="*/5 * * * *", command="echo test")] * 20
configs = [ConfigFile(path=f"/etc/app{i}.conf", service="app") for i in range(5)]

print("Building topology...")
topo = build_topology(packages, services, ports, configs, cron)
print("Components:", len(topo.components))

compose = build_compose(topo)
print("Services in compose:", len(compose.get("services", {})))

output = export_topology(topo, fmt="json")
Path("/tmp/app-map.json").write_text(output)
print("Perf check completed")
PY
