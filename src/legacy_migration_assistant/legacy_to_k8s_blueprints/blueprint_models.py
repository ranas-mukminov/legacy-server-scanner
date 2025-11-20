"""Models used for building Kubernetes manifests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from legacy_migration_assistant.core.models import ComponentType


@dataclass
class BlueprintService:
    """Normalized service description used to generate K8s resources."""

    name: str
    component_type: Optional[ComponentType] = None
    image: Optional[str] = None
    ports: List[int] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    exposed: bool = True


@dataclass
class ResourceAdvice:
    cpu_request: str
    memory_request: str
    cpu_limit: str
    memory_limit: str


@dataclass
class ProbeAdvice:
    liveness: Dict[str, object]
    readiness: Dict[str, object]
    startup: Optional[Dict[str, object]] = None

