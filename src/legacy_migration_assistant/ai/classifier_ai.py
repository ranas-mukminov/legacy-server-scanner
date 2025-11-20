"""Optional AI-assisted classification."""

from __future__ import annotations

import json
from typing import Dict, List

from legacy_migration_assistant.ai.base import AIProvider
from legacy_migration_assistant.core.models import Port, Service


def suggest_classification(provider: AIProvider, services: List[Service], ports: List[Port]) -> Dict[str, str]:
    payload = {
        "services": [svc.name for svc in services],
        "ports": [p.port for p in ports],
    }
    prompt = "Classify services into web/db/cache/queue/cron/support. Return JSON mapping service->type. Data: " + json.dumps(payload)
    raw = provider.complete(prompt)
    try:
        data = json.loads(raw)
        return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}
    except json.JSONDecodeError:
        return {}

