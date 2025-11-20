from legacy_migration_assistant.core.models import AppTopology, AppComponent, ComponentType
from legacy_migration_assistant.legacy_server_scanner.compose_generator import build_compose


def test_compose_generator_creates_services():
    components = [
        AppComponent(name="web", component_type=ComponentType.WEB, ports=[8080], volumes=["/var/www"]),
        AppComponent(name="db", component_type=ComponentType.DATABASE, volumes=["/var/lib/mysql"], depends_on=["web"]),
    ]
    topology = AppTopology(components=components)
    compose = build_compose(topology)
    assert "services" in compose
    assert set(compose["services"].keys()) == {"web", "db"}
