"""Abstract provider interfaces for AI helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class Message:
    role: str
    content: str


class AIProvider(Protocol):
    def complete(self, prompt: str) -> str:
        ...

    def chat(self, messages: List[Message]) -> str:
        ...


class NoopAIProvider:
    """Simple provider that returns TODO-like hints."""

    def complete(self, prompt: str) -> str:
        return f"TODO: review manually -> {prompt[:80]}"

    def chat(self, messages: List[Message]) -> str:
        last = messages[-1].content if messages else ""
        return f"TODO: review manually -> {last[:80]}"

