from legacy_migration_assistant.legacy_to_k8s_blueprints.compose_parser import parse_compose_dict


def test_compose_parser_extracts_ports():
    data = {
        "services": {
            "web": {"image": "nginx", "ports": ["8080:80"]},
            "db": {"image": "mysql", "ports": ["3306:3306"]},
        }
    }
    services = parse_compose_dict(data)
    assert {s.name for s in services} == {"web", "db"}
    assert any(8080 in s.ports for s in services if s.name == "web")
