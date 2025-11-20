"""Probe heuristics for Kubernetes workloads."""

from __future__ import annotations

from typing import Dict

from legacy_migration_assistant.core.models import ComponentType
from legacy_migration_assistant.legacy_to_k8s_blueprints.blueprint_models import ProbeAdvice


def _http_probe(path: str, port: int) -> Dict[str, object]:
    return {"httpGet": {"path": path, "port": port}, "initialDelaySeconds": 10, "periodSeconds": 10}


def _tcp_probe(port: int) -> Dict[str, object]:
    return {"tcpSocket": {"port": port}, "initialDelaySeconds": 10, "periodSeconds": 10}


def suggest_probes(component_type: ComponentType | None, ports: list[int]) -> ProbeAdvice:
    port = ports[0] if ports else 80
    if component_type == ComponentType.WEB:
        return ProbeAdvice(liveness=_http_probe("/health", port), readiness=_http_probe("/", port), startup=None)
    if component_type == ComponentType.DATABASE:
        return ProbeAdvice(liveness=_tcp_probe(port), readiness=_tcp_probe(port), startup=None)
    if component_type == ComponentType.CACHE:
        return ProbeAdvice(liveness=_tcp_probe(port), readiness=_tcp_probe(port), startup=None)
    if component_type == ComponentType.QUEUE:
        return ProbeAdvice(liveness=_tcp_probe(port), readiness=_tcp_probe(port), startup=None)
    return ProbeAdvice(liveness=_tcp_probe(port), readiness=_tcp_probe(port), startup=None)

