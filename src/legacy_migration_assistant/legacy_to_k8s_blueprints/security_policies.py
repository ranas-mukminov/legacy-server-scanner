"""Baseline security templates."""

from __future__ import annotations

from typing import Dict, List


def pod_security_context() -> Dict[str, object]:
    return {"runAsNonRoot": True, "runAsUser": 1000, "fsGroup": 1000}


def container_security_context() -> Dict[str, object]:
    return {"allowPrivilegeEscalation": False, "readOnlyRootFilesystem": False}


def service_account_manifest(name: str, namespace: str) -> Dict[str, object]:
    return {"apiVersion": "v1", "kind": "ServiceAccount", "metadata": {"name": name, "namespace": namespace}}


def network_policy_allow_namespace(app: str, namespace: str, ports: List[int]) -> Dict[str, object]:
    ingress_rules = []
    if ports:
        ingress_rules.append({"ports": [{"protocol": "TCP", "port": p} for p in ports]})
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {"name": f"{app}-default-allow", "namespace": namespace},
        "spec": {
            "podSelector": {"matchLabels": {"app": app}},
            "policyTypes": ["Ingress"],
            "ingress": ingress_rules or [{"from": [{"namespaceSelector": {}}]}],
        },
    }

