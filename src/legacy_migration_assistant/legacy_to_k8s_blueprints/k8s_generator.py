"""Generate Kubernetes manifests from blueprint services."""

from __future__ import annotations

from typing import Dict, List, Optional

import yaml

from legacy_migration_assistant.legacy_to_k8s_blueprints.blueprint_models import BlueprintService
from legacy_migration_assistant.legacy_to_k8s_blueprints import security_policies
from legacy_migration_assistant.legacy_to_k8s_blueprints.resources_advisor import suggest_resources
from legacy_migration_assistant.legacy_to_k8s_blueprints.probes_advisor import suggest_probes


def _container_name(service: BlueprintService) -> str:
    return service.name.replace("_", "-")


def build_deployment(service: BlueprintService, namespace: str = "default") -> Dict[str, object]:
    resources = suggest_resources(service.component_type)
    probes = suggest_probes(service.component_type, service.ports)
    container = {
        "name": _container_name(service),
        "image": service.image or "TODO: provide image",
        "ports": [{"containerPort": p} for p in service.ports] if service.ports else [],
        "env": [{"name": k, "value": v} for k, v in service.environment.items()],
        "resources": {
            "requests": {"cpu": resources.cpu_request, "memory": resources.memory_request},
            "limits": {"cpu": resources.cpu_limit, "memory": resources.memory_limit},
        },
        "livenessProbe": probes.liveness,
        "readinessProbe": probes.readiness,
    }
    if probes.startup:
        container["startupProbe"] = probes.startup
    if service.volumes:
        container["volumeMounts"] = [{"name": f"data-{idx}", "mountPath": path} for idx, path in enumerate(service.volumes)]
    template = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": service.name, "namespace": namespace, "labels": {"app": service.name}},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": service.name}},
            "template": {
                "metadata": {"labels": {"app": service.name}},
                "spec": {
                    "serviceAccountName": service.name,
                    "securityContext": security_policies.pod_security_context(),
                    "containers": [container],
                },
            },
        },
    }
    if service.volumes:
        template["spec"]["template"]["spec"]["volumes"] = [
            {"name": f"data-{idx}", "emptyDir": {}} for idx, _ in enumerate(service.volumes)
        ]
    return template


def build_service(service: BlueprintService, namespace: str = "default") -> Dict[str, object]:
    ports = [{"port": p, "targetPort": p, "protocol": "TCP"} for p in service.ports] or [{"port": 80, "targetPort": 80}]
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": service.name, "namespace": namespace, "labels": {"app": service.name}},
        "spec": {
            "type": "ClusterIP",
            "selector": {"app": service.name},
            "ports": ports,
        },
    }


def build_ingress(services: List[BlueprintService], host: str, namespace: str = "default") -> Dict[str, object]:
    rules = []
    for svc in services:
        if not svc.ports:
            continue
        rules.append(
            {
                "path": "/",
                "pathType": "Prefix",
                "backend": {"service": {"name": svc.name, "port": {"number": svc.ports[0]}}},
            }
        )
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {"name": "legacy-migration", "namespace": namespace},
        "spec": {"rules": [{"host": host, "http": {"paths": rules}}]},
    }


def generate_manifests(
    services: List[BlueprintService],
    namespace: str = "default",
    ingress_host: Optional[str] = None,
) -> Dict[str, str]:
    rendered: Dict[str, str] = {}
    for svc in services:
        deployment = build_deployment(svc, namespace)
        service = build_service(svc, namespace)
        sa = security_policies.service_account_manifest(svc.name, namespace)
        netpol = security_policies.network_policy_allow_namespace(svc.name, namespace, svc.ports)
        rendered[f"deployment-{svc.name}.yaml"] = yaml.safe_dump(deployment, sort_keys=False)
        rendered[f"service-{svc.name}.yaml"] = yaml.safe_dump(service, sort_keys=False)
        rendered[f"sa-{svc.name}.yaml"] = yaml.safe_dump(sa, sort_keys=False)
        rendered[f"netpol-{svc.name}.yaml"] = yaml.safe_dump(netpol, sort_keys=False)
    if ingress_host:
        ingress = build_ingress(services, ingress_host, namespace)
        rendered["ingress.yaml"] = yaml.safe_dump(ingress, sort_keys=False)
    return rendered

