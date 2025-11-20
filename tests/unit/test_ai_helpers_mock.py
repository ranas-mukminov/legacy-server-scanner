from legacy_migration_assistant.ai.base import NoopAIProvider, Message
from legacy_migration_assistant.ai.compose_ai_helper import generate_compose_comments
from legacy_migration_assistant.core.models import AppTopology, AppComponent, ComponentType


def test_noop_provider():
    provider = NoopAIProvider()
    result = provider.complete("hello")
    assert "TODO" in result


def test_compose_comments():
    topo = AppTopology(components=[AppComponent(name="web", component_type=ComponentType.WEB)])
    comments = generate_compose_comments(topo)
    assert comments and comments[0].startswith("TODO")


def test_chat_noop():
    provider = NoopAIProvider()
    reply = provider.chat([Message(role="user", content="hi")])
    assert "TODO" in reply
