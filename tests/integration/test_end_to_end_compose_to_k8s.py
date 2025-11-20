import yaml

from legacy_migration_assistant.legacy_to_k8s_blueprints.compose_parser import parse_compose_dict
from legacy_migration_assistant.legacy_to_k8s_blueprints.k8s_generator import generate_manifests


def test_compose_to_k8s_generation():
    compose = {
        "services": {
            "web": {"image": "nginx", "ports": ["8080:80"]},
            "db": {"image": "postgres", "ports": ["5432:5432"]},
        }
    }
    blueprint = parse_compose_dict(compose)
    manifests = generate_manifests(blueprint, namespace="demo", ingress_host="demo.local")
    assert any(name.startswith("deployment-web") for name in manifests)
    for content in manifests.values():
        yaml.safe_load(content)
