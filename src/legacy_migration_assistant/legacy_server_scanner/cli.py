"""CLI for legacy-server-scanner."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import yaml

from legacy_migration_assistant.core.models import (
    AppComponent,
    AppTopology,
    ComponentType,
    ConfigFile,
    CronJob,
    Package,
    Port,
    Relation,
    Service,
)
from legacy_migration_assistant.legacy_server_scanner import compose_generator, exporter
from legacy_migration_assistant.legacy_server_scanner.configs import discover_configs
from legacy_migration_assistant.legacy_server_scanner.cron import collect_cron
from legacy_migration_assistant.legacy_server_scanner.packages import collect_packages
from legacy_migration_assistant.legacy_server_scanner.ports import collect_ports
from legacy_migration_assistant.legacy_server_scanner.services import collect_services
from legacy_migration_assistant.legacy_server_scanner.topology_builder import build_topology


def _serialize_scan(packages, services, ports, cron_jobs, configs) -> Dict[str, Any]:
    return {
        "packages": [asdict(p) for p in packages],
        "services": [asdict(s) for s in services],
        "ports": [asdict(p) for p in ports],
        "cron": [asdict(c) for c in cron_jobs],
        "configs": [asdict(c) for c in configs],
    }


def _deserialize_list(data: List[Dict[str, Any]], cls):
    return [cls(**item) for item in data]


def command_scan(args: argparse.Namespace) -> None:
    packages = collect_packages()
    services = collect_services()
    ports = collect_ports()
    cron_jobs = collect_cron()
    configs = discover_configs()

    scan_payload = _serialize_scan(packages, services, ports, cron_jobs, configs)
    Path(args.output).write_text(json.dumps(scan_payload, indent=2), encoding="utf-8")
    print(f"Scan saved to {args.output}")


def command_map(args: argparse.Namespace) -> None:
    raw = json.loads(Path(args.scan).read_text(encoding="utf-8"))
    packages = _deserialize_list(raw.get("packages", []), Package)
    services = _deserialize_list(raw.get("services", []), Service)
    ports = _deserialize_list(raw.get("ports", []), Port)
    cron_jobs = _deserialize_list(raw.get("cron", []), CronJob)
    configs = _deserialize_list(raw.get("configs", []), ConfigFile)

    topology = build_topology(packages, services, ports, configs, cron_jobs)
    exporter.save_topology(topology, args.output, fmt="yaml")
    print(f"Application map saved to {args.output}")


def _topology_from_dict(data: Dict[str, Any]) -> AppTopology:
    components = [
        AppComponent(
            name=item["name"],
            component_type=ComponentType(item["component_type"]),
            ports=item.get("ports", []),
            volumes=item.get("volumes", []),
            environment=item.get("environment", {}),
            depends_on=item.get("depends_on", []),
            notes=item.get("notes", []),
        )
        for item in data.get("components", [])
    ]
    relations = [
        Relation(source=item["source"], target=item["target"], description=item.get("description"))
        for item in data.get("relations", [])
    ]
    packages = _deserialize_list(data.get("packages", []), Package)
    services = _deserialize_list(data.get("services", []), Service)
    ports = _deserialize_list(data.get("ports", []), Port)
    cron_jobs = _deserialize_list(data.get("cron", []), CronJob)
    configs = _deserialize_list(data.get("configs", []), ConfigFile)

    # Components and relations are simple structures; reuse dictionaries directly
    topo = AppTopology(
        components=components,
        relations=relations,
        packages=packages,
        services=services,
        ports=ports,
        cron=cron_jobs,
        configs=configs,
    )
    return topo


def command_compose(args: argparse.Namespace) -> None:
    content = Path(args.map).read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    topology = _topology_from_dict(data)
    compose = compose_generator.build_compose(topology)
    rendered = compose_generator.compose_to_yaml(compose)
    Path(args.output).write_text(rendered, encoding="utf-8")
    print(f"Docker compose saved to {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Legacy server scanner")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Collect raw scan data")
    scan.add_argument("--output", required=True, help="Path to write scan.json")
    scan.set_defaults(func=command_scan)

    map_cmd = sub.add_parser("map", help="Build application map from scan")
    map_cmd.add_argument("--scan", required=True, help="Path to scan.json")
    map_cmd.add_argument("--output", required=True, help="Path to app-map.yaml output")
    map_cmd.set_defaults(func=command_map)

    compose_cmd = sub.add_parser("compose", help="Generate docker-compose from map")
    compose_cmd.add_argument("--map", required=True, help="Path to app-map.yaml")
    compose_cmd.add_argument("--output", required=True, help="Path to docker-compose.yaml")
    compose_cmd.set_defaults(func=command_compose)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
