from legacy_migration_assistant.core.models import (
    ComponentType,
    ConfigFile,
    CronJob,
    Package,
    Port,
    Service,
)
from legacy_migration_assistant.legacy_server_scanner.topology_builder import build_topology


def test_build_topology_basic():
    packages = [Package(name="nginx", version="1.0"), Package(name="mysql", version="1.0")]
    services = [Service(name="nginx", status="running"), Service(name="mysql", status="running")]
    ports = [Port(protocol="tcp", address="0.0.0.0", port=80), Port(protocol="tcp", address="0.0.0.0", port=3306)]
    configs = [ConfigFile(path="/etc/nginx/nginx.conf", service="nginx")]
    cron_jobs = [CronJob(schedule="0 1 * * *", command="echo test")]

    topology = build_topology(packages, services, ports, configs, cron_jobs)
    types = {c.component_type for c in topology.components}
    assert ComponentType.WEB in types
    assert any(rel.target == "db" or rel.description for rel in topology.relations)
