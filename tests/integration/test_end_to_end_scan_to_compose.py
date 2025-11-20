from legacy_migration_assistant.core.models import Package, Service, Port, ConfigFile, CronJob
from legacy_migration_assistant.legacy_server_scanner.topology_builder import build_topology
from legacy_migration_assistant.legacy_server_scanner.compose_generator import build_compose


def test_scan_to_compose_pipeline():
    packages = [Package(name="nginx", version="1.0"), Package(name="mysql", version="8.0")]
    services = [Service(name="nginx", status="running"), Service(name="mysql", status="running")]
    ports = [Port(protocol="tcp", address="0.0.0.0", port=80), Port(protocol="tcp", address="0.0.0.0", port=3306)]
    configs = [ConfigFile(path="/etc/nginx/nginx.conf", service="nginx")]
    cron_jobs = [CronJob(schedule="0 1 * * *", command="echo test")]

    topology = build_topology(packages, services, ports, configs, cron_jobs)
    compose = build_compose(topology)

    assert "web" in compose["services"] and "db" in compose["services"]
