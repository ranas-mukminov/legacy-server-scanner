from legacy_migration_assistant.core.models import ComponentType
from legacy_migration_assistant.legacy_to_k8s_blueprints.blueprint_models import BlueprintService
from legacy_migration_assistant.legacy_to_k8s_blueprints.k8s_generator import build_deployment, build_service


def test_deployment_contains_resources_and_probes():
    svc = BlueprintService(name='web', component_type=ComponentType.WEB, ports=[8080])
    dep = build_deployment(svc, namespace='demo')
    assert dep['kind'] == 'Deployment'
    container = dep['spec']['template']['spec']['containers'][0]
    assert 'resources' in container and 'livenessProbe' in container


def test_service_ports():
    svc = BlueprintService(name='db', component_type=ComponentType.DATABASE, ports=[5432])
    manifest = build_service(svc, namespace='demo')
    assert manifest['spec']['ports'][0]['port'] == 5432
