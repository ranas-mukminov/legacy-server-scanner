"""Build an application topology from collected scan data."""

from __future__ import annotations

from typing import List

from legacy_migration_assistant.core.models import (
    AppComponent,
    AppTopology,
    ComponentType,
    CronJob,
    Package,
    Port,
    Relation,
    Service,
    ConfigFile,
)
from legacy_migration_assistant.legacy_server_scanner.classifier import classify_components


def build_relations(components: List[AppComponent]) -> List[Relation]:
    """Best-effort dependency mapping between components."""

    names = {c.component_type: c.name for c in components}
    relations: List[Relation] = []

    if ComponentType.WEB in names and ComponentType.DATABASE in names:
        relations.append(
            Relation(
                source=names[ComponentType.WEB],
                target=names[ComponentType.DATABASE],
                description="web connects to database",
            )
        )
    if ComponentType.WEB in names and ComponentType.CACHE in names:
        relations.append(
            Relation(
                source=names[ComponentType.WEB],
                target=names[ComponentType.CACHE],
                description="web uses cache",
            )
        )
    if ComponentType.WORKER in names and ComponentType.QUEUE in names:
        relations.append(
            Relation(
                source=names[ComponentType.WORKER],
                target=names[ComponentType.QUEUE],
                description="worker consumes queue",
            )
        )

    return relations


def build_topology(
    packages: List[Package],
    services: List[Service],
    ports: List[Port],
    configs: List[ConfigFile],
    cron_jobs: List[CronJob],
) -> AppTopology:
    """Create an AppTopology from scan results."""

    components = classify_components(packages, services, ports, configs)
    for component in components:
        if component.component_type == ComponentType.CRON and cron_jobs:
            component.notes.append(f"{len(cron_jobs)} cron entries detected")
    relations = build_relations(components)
    return AppTopology(
        components=components,
        relations=relations,
        packages=packages,
        services=services,
        ports=ports,
        cron=cron_jobs,
        configs=configs,
    )
