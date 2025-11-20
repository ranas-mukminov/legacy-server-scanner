"""Export application topology to YAML or JSON formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml

from legacy_migration_assistant.core.models import AppTopology


def export_topology(topology: AppTopology, fmt: Literal["json", "yaml"] = "yaml") -> str:
    """Serialize topology to a string."""

    data = topology.to_dict()
    if fmt == "json":
        return json.dumps(data, indent=2)
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)


def save_topology(topology: AppTopology, path: str, fmt: Literal["json", "yaml"] = "yaml") -> None:
    """Serialize and write topology to file."""

    formatted = export_topology(topology, fmt)
    Path(path).write_text(formatted, encoding="utf-8")

