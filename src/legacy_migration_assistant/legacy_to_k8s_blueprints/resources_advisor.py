"""Resource heuristics for components."""

from __future__ import annotations

from legacy_migration_assistant.core.models import ComponentType
from legacy_migration_assistant.legacy_to_k8s_blueprints.blueprint_models import ResourceAdvice

DEFAULT = ResourceAdvice(
    cpu_request="100m",
    memory_request="128Mi",
    cpu_limit="500m",
    memory_limit="256Mi",
)


def suggest_resources(component_type: ComponentType | None) -> ResourceAdvice:
    if component_type == ComponentType.WEB:
        return ResourceAdvice("200m", "256Mi", "500m", "512Mi")
    if component_type == ComponentType.DATABASE:
        return ResourceAdvice("500m", "512Mi", "1", "1Gi")
    if component_type == ComponentType.CACHE:
        return ResourceAdvice("200m", "256Mi", "500m", "512Mi")
    if component_type == ComponentType.QUEUE:
        return ResourceAdvice("200m", "256Mi", "500m", "512Mi")
    if component_type == ComponentType.WORKER:
        return ResourceAdvice("300m", "256Mi", "700m", "512Mi")
    return DEFAULT

