"""CLI for generating Kubernetes blueprints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

from legacy_migration_assistant.core.models import (
    AppComponent,
    AppTopology,
    ComponentType,
    Relation,
)
from legacy_migration_assistant.legacy_to_k8s_blueprints.compose_parser import (
    parse_compose_file,
    topology_to_blueprint,
)
from legacy_migration_assistant.legacy_to_k8s_blueprints.k8s_generator import generate_manifests


def _ensure_output_dir(path: str) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


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
    topology = AppTopology(
        components=components,
        relations=relations,
        packages=data.get("packages", []),
        services=data.get("services", []),
        ports=data.get("ports", []),
        cron=data.get("cron", []),
        configs=data.get("configs", []),
    )
    return topology


def command_from_compose(args: argparse.Namespace) -> None:
    blueprint = parse_compose_file(args.compose)
    manifests = generate_manifests(blueprint, namespace=args.namespace, ingress_host=args.ingress_host)
    out = _ensure_output_dir(args.output_dir)
    for name, content in manifests.items():
        (out / name).write_text(content, encoding="utf-8")
    print(f"K8s manifests written to {out}")


def command_from_map(args: argparse.Namespace) -> None:
    raw_content = Path(args.map).read_text(encoding="utf-8")
    data = yaml.safe_load(raw_content) if args.map.endswith((".yml", ".yaml")) else json.loads(raw_content)
    topology = _topology_from_dict(data or {})
    blueprint = topology_to_blueprint(topology)
    manifests = generate_manifests(blueprint, namespace=args.namespace, ingress_host=args.ingress_host)
    out = _ensure_output_dir(args.output_dir)
    for name, content in manifests.items():
        (out / name).write_text(content, encoding="utf-8")
    print(f"K8s manifests written to {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="legacy-to-k8s-blueprints")
    sub = parser.add_subparsers(dest="command", required=True)

    compose_cmd = sub.add_parser("from-compose", help="Generate from docker-compose")
    compose_cmd.add_argument("--compose", required=True, help="Path to docker-compose.yml")
    compose_cmd.add_argument("--output-dir", required=True, help="Directory for manifests")
    compose_cmd.add_argument("--namespace", default="default")
    compose_cmd.add_argument("--ingress-host", default=None)
    compose_cmd.set_defaults(func=command_from_compose)

    map_cmd = sub.add_parser("from-map", help="Generate from application map")
    map_cmd.add_argument("--map", required=True, help="Path to app-map.yaml")
    map_cmd.add_argument("--output-dir", required=True, help="Directory for manifests")
    map_cmd.add_argument("--namespace", default="default")
    map_cmd.add_argument("--ingress-host", default=None)
    map_cmd.set_defaults(func=command_from_map)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

