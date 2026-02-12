from dataclasses import dataclass
from typing import List, Optional, Literal

from .checker import HealthChecker
from .storage import Storage
from .models import CheckResult, Status


@dataclass
class Transition:
    from_status: Status
    to_status: Status
    timestamp: str


@dataclass
class CycleResult:
    result: CheckResult
    transition: Optional[Transition]


class Monitor:
    def __init__(self, storage: Storage, checker: HealthChecker, urls: List[str]):
        self.storage = storage
        self.checker = checker
        self.urls = urls

    def run_cycle(self) -> List[CycleResult]:
        results: List[CycleResult] = []

        for url in self.urls:
            previous = self.storage.get_last_check(url)
            current = self.checker.check(url)

            transition = self._detect_transition(previous, current)

            # persist raw check only
            self.storage.insert_check(current)

            if transition:
                self._alert_transition(url, transition)

            results.append(CycleResult(result=current, transition=transition))

        return results

    def _detect_transition(
        self,
        previous: Optional[CheckResult],
        current: CheckResult,
    ) -> Optional[Transition]:
        if not previous:
            return None

        if previous.status != current.status:
            return Transition(
                from_status=previous.status,
                to_status=current.status,
                timestamp=current.timestamp,
            )

        return None

    def _alert_transition(self, url: str, transition: Transition) -> None:
        print(
            f"ALERT: {url} transitioned "
            f"{transition.from_status} → {transition.to_status}"
        )

    def get_report(self, url: str):
        return self.storage.get_summary(url)

    def get_history(self, url: str, limit: int = 20) -> List[CheckResult]:
        return self.storage.get_history(url, limit=limit)
