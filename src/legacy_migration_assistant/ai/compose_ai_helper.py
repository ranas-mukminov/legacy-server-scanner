"""Compose helper that can add human-readable hints."""

from __future__ import annotations

from typing import List

from legacy_migration_assistant.ai.base import AIProvider, NoopAIProvider
from legacy_migration_assistant.core.models import AppTopology


def generate_compose_comments(topology: AppTopology, provider: AIProvider | None = None) -> List[str]:
    provider = provider or NoopAIProvider()
    summary = ", ".join([f"{c.name}({c.component_type.value})" for c in topology.components])
    prompt = f"Provide migration hints for compose services: {summary}"
    text = provider.complete(prompt)
    return [text]

