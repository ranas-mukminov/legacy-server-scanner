from legacy_migration_assistant.core.models import ComponentType
from legacy_migration_assistant.legacy_to_k8s_blueprints.resources_advisor import suggest_resources


def test_resources_for_web():
    res = suggest_resources(ComponentType.WEB)
    assert res.cpu_request == "200m"
    assert res.memory_limit.endswith("Mi") or res.memory_limit.endswith("Gi")
