from legacy_migration_assistant.core.models import ComponentType
from legacy_migration_assistant.legacy_to_k8s_blueprints.probes_advisor import suggest_probes


def test_web_probes_http():
    probes = suggest_probes(ComponentType.WEB, [8080])
    assert 'httpGet' in probes.liveness
    assert probes.liveness['httpGet']['port'] == 8080
