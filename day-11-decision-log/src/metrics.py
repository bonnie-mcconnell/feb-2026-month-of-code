from collections import Counter
from typing import Iterable

from .models import Decision
from .outcomes import Outcome


def count_by_actor(decisions: Iterable[Decision]) -> dict[str, int]:
    return dict(Counter(d.actor for d in decisions))


def count_by_tag(decisions: Iterable[Decision]) -> dict[str, int]:
    counter = Counter()
    for d in decisions:
        for tag in d.tags:
            counter[tag] += 1
    return dict(counter)


def decision_count(decisions: Iterable[Decision]) -> int:
    return sum(1 for _ in decisions)


def outcome_count(outcomes: Iterable[Outcome]) -> int:
    return sum(1 for _ in outcomes)
