"""Shared data models for legacy migration assistant."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class OSFamily(str, Enum):
    """High-level OS family."""

    DEBIAN = "debian"
    RHEL = "rhel"
    OTHER = "other"


@dataclass
class OSRelease:
    """Information parsed from /etc/os-release."""

    id: str
    version_id: str
    pretty_name: Optional[str] = None


@dataclass
class Package:
    """Installed package information."""

    name: str
    version: str
    source: Optional[str] = None


@dataclass
class Service:
    """Running service description."""

    name: str
    status: str
    main_cmd: Optional[str] = None
    manager: Optional[str] = None
    pid: Optional[int] = None


@dataclass
class Port:
    """Network port binding."""

    protocol: str
    address: str
    port: int
    process: Optional[str] = None
    pid: Optional[int] = None


@dataclass
class CronJob:
    """Cron schedule entry."""

    schedule: str
    command: str
    user: Optional[str] = None
    source: Optional[str] = None


@dataclass
class ConfigFile:
    """Configuration file reference."""

    path: str
    service: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComponentType(str, Enum):
    """Type classifier for application components."""

    WEB = "web"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    CRON = "cron"
    WORKER = "worker"
    SUPPORT = "support"
    OTHER = "other"


@dataclass
class AppComponent:
    """Application component with connectivity metadata."""

    name: str
    component_type: ComponentType
    ports: List[int] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class Relation:
    """Directed relation between components."""

    source: str
    target: str
    description: Optional[str] = None


@dataclass
class AppTopology:
    """Application map produced by the scanner."""

    components: List[AppComponent] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    packages: List[Package] = field(default_factory=list)
    services: List[Service] = field(default_factory=list)
    ports: List[Port] = field(default_factory=list)
    cron: List[CronJob] = field(default_factory=list)
    configs: List[ConfigFile] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a serializable dictionary."""
        return asdict(self)

