"""Parse docker-compose into an internal blueprint model."""

from __future__ import annotations

from typing import Dict, List

import yaml

from legacy_migration_assistant.core.models import AppTopology
from legacy_migration_assistant.legacy_to_k8s_blueprints.blueprint_models import BlueprintService


def _extract_ports(port_entries: List[object]) -> List[int]:
    ports: List[int] = []
    for entry in port_entries:
        text = str(entry)
        if ":" in text:
            host, _, container = text.rpartition(":")
            target = host or container
            try:
                ports.append(int(target))
            except ValueError:
                continue
        else:
            try:
                ports.append(int(text))
            except ValueError:
                continue
    return sorted({p for p in ports if p > 0})


def parse_compose_dict(data: Dict[str, object]) -> List[BlueprintService]:
    services: List[BlueprintService] = []
    for name, raw in data.get("services", {}).items():
        if not isinstance(raw, dict):
            continue
        ports = _extract_ports(raw.get("ports", []))
        env_raw = raw.get("environment", {}) or {}
        environment = {str(k): str(v) for k, v in env_raw.items()} if isinstance(env_raw, dict) else {}
        volumes = [str(v) for v in raw.get("volumes", []) or []]
        depends_on = list(raw.get("depends_on", []) or [])
        services.append(
            BlueprintService(
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                depends_on=depends_on,
                image=raw.get("image"),
            )
        )
    return services


def parse_compose_file(path: str) -> List[BlueprintService]:
    content = yaml.safe_load(open(path, "r", encoding="utf-8"))
    return parse_compose_dict(content or {})


def topology_to_blueprint(topology: AppTopology) -> List[BlueprintService]:
    services: List[BlueprintService] = []
    name_to_component: Dict[str, object] = {c.name: c for c in topology.components}
    for comp in topology.components:
        depends = list(comp.depends_on)
        services.append(
            BlueprintService(
                name=comp.name,
                component_type=comp.component_type,
                ports=comp.ports,
                environment=comp.environment,
                volumes=comp.volumes,
                depends_on=depends,
            )
        )
    # Infer relations dependencies if missing
    for rel in topology.relations:
        source_component = name_to_component.get(rel.source)
        if not source_component:
            continue
        match = next((svc for svc in services if svc.name == rel.source), None)
        if match and rel.target not in match.depends_on:
            match.depends_on.append(rel.target)
    return services

