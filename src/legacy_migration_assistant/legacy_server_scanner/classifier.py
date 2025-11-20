"""Heuristic classification of discovered services into components."""

from __future__ import annotations

from typing import List

from legacy_migration_assistant.core.models import (
    AppComponent,
    ComponentType,
    ConfigFile,
    Package,
    Port,
    Service,
)


def _has_name(names: List[str], needles: List[str]) -> bool:
    lowered = [n.lower() for n in names]
    return any(needle in entry for entry in lowered for needle in needles)


def classify_components(
    packages: List[Package], services: List[Service], ports: List[Port], configs: List[ConfigFile]
) -> List[AppComponent]:
    components: List[AppComponent] = []

    if _has_name([svc.name for svc in services] + [cfg.service for cfg in configs], ["nginx", "apache"]):
        web_ports = [p.port for p in ports if p.port in (80, 443)] or [80]
        components.append(
            AppComponent(
                name="web",
                component_type=ComponentType.WEB,
                ports=web_ports,
                notes=["Detected web server (nginx/apache)"]
            )
        )

    if _has_name([pkg.name for pkg in packages] + [svc.name for svc in services], ["php"]):
        components.append(
            AppComponent(
                name="app",
                component_type=ComponentType.WORKER,
                notes=["PHP runtime detected"],
                depends_on=["web"] if any(c.name == "web" for c in components) else [],
            )
        )

    if _has_name([svc.name for svc in services], ["mysql", "mariadb"]):
        components.append(
            AppComponent(
                name="db",
                component_type=ComponentType.DATABASE,
                ports=[3306],
                volumes=["/var/lib/mysql"],
                notes=["MySQL/MariaDB detected"],
            )
        )
    if _has_name([svc.name for svc in services], ["postgres", "postgresql"]):
        components.append(
            AppComponent(
                name="postgres",
                component_type=ComponentType.DATABASE,
                ports=[5432],
                volumes=["/var/lib/postgresql"],
                notes=["PostgreSQL detected"],
            )
        )

    if _has_name([svc.name for svc in services], ["redis"]):
        components.append(
            AppComponent(
                name="redis",
                component_type=ComponentType.CACHE,
                ports=[6379],
                volumes=["/var/lib/redis"],
            )
        )
    if _has_name([svc.name for svc in services], ["memcached"]):
        components.append(AppComponent(name="memcached", component_type=ComponentType.CACHE, ports=[11211]))
    if _has_name([svc.name for svc in services], ["rabbitmq"]):
        components.append(
            AppComponent(
                name="queue",
                component_type=ComponentType.QUEUE,
                ports=[5672, 15672],
                volumes=["/var/lib/rabbitmq"],
            )
        )

    if _has_name([svc.name for svc in services], ["cron", "crond"]):
        components.append(AppComponent(name="cron", component_type=ComponentType.CRON))

    for svc in services:
        if svc.name in {"sshd", "rsyslog", "systemd-logind"}:
            components.append(
                AppComponent(name=svc.name, component_type=ComponentType.SUPPORT, notes=["Infrastructure"])
            )

    return components
