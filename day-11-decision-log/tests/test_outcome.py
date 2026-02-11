from pathlib import Path
import tempfile
import json
import pytest

from src.models import Decision
from src.outcomes import Outcome, load_all, append as append_outcome

def test_outcome_append_only(tmp_path: Path):
    # Create a decision
    decision = Decision.create(
        actor="alice",
        title="Test decision",
        description="Testing outcome system",
        context="unit test",
        inputs={"foo": "bar"}
    )

    outcome_file = tmp_path / "outcomes.json"

    # Append first outcome
    outcome1 = Outcome.create(decision_id=decision.decision_id, outcome="success")
    append_outcome(outcome1, outcome_file)

    # Append second outcome
    outcome2 = Outcome.create(decision_id=decision.decision_id, outcome="needs review")
    append_outcome(outcome2, outcome_file)

    # Load and validate
    loaded = load_all(outcome_file)
    assert len(loaded) == 2
    assert loaded[0].outcome == "success"
    assert loaded[1].outcome == "needs review"
    assert all(o.decision_id == decision.decision_id for o in loaded)
