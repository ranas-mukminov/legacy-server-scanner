"""AI hints for Kubernetes manifests."""

from __future__ import annotations

from typing import List

from legacy_migration_assistant.ai.base import AIProvider, NoopAIProvider
from legacy_migration_assistant.legacy_to_k8s_blueprints.blueprint_models import BlueprintService


def advise_resources(services: List[BlueprintService], provider: AIProvider | None = None) -> str:
    provider = provider or NoopAIProvider()
    names = ", ".join(svc.name for svc in services)
    prompt = f"Suggest resource tuning for services: {names}. Keep it brief."
    return provider.complete(prompt)


def advise_annotations(service: BlueprintService, provider: AIProvider | None = None) -> str:
    provider = provider or NoopAIProvider()
    prompt = f"Suggest useful ingress/monitoring annotations for service {service.name}"
    return provider.complete(prompt)

