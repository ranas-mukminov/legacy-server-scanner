"""Generate draft docker-compose configuration from an application topology."""

from __future__ import annotations

from typing import Dict, List

import yaml

from legacy_migration_assistant.core.models import AppTopology


def _build_service_ports(ports: List[int]) -> List[str]:
    return [f"{port}:{port}" for port in ports]


def _relations_dependencies(topology: AppTopology, name: str) -> List[str]:
    deps = {rel.target for rel in topology.relations if rel.source == name}
    return sorted(deps)


def build_compose(topology: AppTopology) -> Dict[str, object]:
    """Create docker-compose structure from topology."""

    services: Dict[str, Dict[str, object]] = {}
    volumes: Dict[str, Dict[str, object]] = {}

    for component in topology.components:
        service: Dict[str, object] = {
            "image": "TODO: choose image",
        }
        if component.ports:
            service["ports"] = _build_service_ports(component.ports)
        if component.volumes:
            mount_names = []
            for idx, vol in enumerate(component.volumes):
                name = f"{component.name}-data-{idx}"
                volumes[name] = {"driver": "local"}
                mount_names.append(f"{name}:{vol}")
            service["volumes"] = mount_names
        if component.environment:
            safe_env = {k: v for k, v in component.environment.items() if "key" not in k.lower() and "pass" not in k.lower()}
            if safe_env:
                service["environment"] = safe_env
        depends = set(component.depends_on) | set(_relations_dependencies(topology, component.name))
        if depends:
            service["depends_on"] = sorted(depends)
        if component.notes:
            service["x-notes"] = component.notes
        service["restart"] = "unless-stopped"
        services[component.name] = service

    compose: Dict[str, object] = {
        "version": "3.9",
        "services": services,
    }
    if volumes:
        compose["volumes"] = volumes
    return compose


def compose_to_yaml(compose: Dict[str, object]) -> str:
    """Render compose dict to YAML."""

    return yaml.safe_dump(compose, sort_keys=False)

