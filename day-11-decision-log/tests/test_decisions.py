from pathlib import Path
import json

import pytest

from src.models import Decision
from src.log import record_decision
from src.query import (
    load_decisions,
    filter_by_actor,
    filter_by_tag,
)
from src.storage import load_all


def test_decision_creation_generates_id_and_timestamp():
    decision = Decision.create(
        actor="test-user",
        title="Test decision",
        description="Testing decision creation",
        context="Unit test",
        inputs={"a": 1},
    )

    assert decision.decision_id
    assert decision.timestamp
    assert decision.actor == "test-user"


def test_decision_is_immutable():
    decision = Decision.create(
        actor="test-user",
        title="Immutable decision",
        description="Should not be mutable",
        context="Unit test",
        inputs={},
    )

    with pytest.raises(Exception):
        decision.title = "mutated"


def test_append_only_storage(tmp_path: Path):
    storage_path = tmp_path / "decisions.json"

    first = record_decision(
        actor="system",
        title="First",
        description="First decision",
        context="Test",
        inputs={},
        storage_path=storage_path,
    )

    second = record_decision(
        actor="system",
        title="Second",
        description="Second decision",
        context="Test",
        inputs={},
        storage_path=storage_path,
    )

    decisions = load_all(storage_path)
    assert len(decisions) == 2
    assert decisions[0].decision_id == first.decision_id
    assert decisions[1].decision_id == second.decision_id


def test_query_by_actor_and_tag(tmp_path: Path):
    storage_path = tmp_path / "decisions.json"

    record_decision(
        actor="alice",
        title="Tagged decision",
        description="Has tag",
        context="Test",
        inputs={},
        tags=["important"],
        storage_path=storage_path,
    )

    record_decision(
        actor="bob",
        title="Untagged decision",
        description="No tag",
        context="Test",
        inputs={},
        storage_path=storage_path,
    )

    decisions = load_decisions(storage_path)

    alice_only = filter_by_actor(decisions, "alice")
    assert len(alice_only) == 1

    tagged = filter_by_tag(decisions, "important")
    assert len(tagged) == 1
    assert tagged[0].actor == "alice"
