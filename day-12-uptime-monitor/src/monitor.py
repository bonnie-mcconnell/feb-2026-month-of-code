from typing import List, Optional, Dict

from .checker import HealthChecker
from .storage import Storage
from .models import CheckResult


class Monitor:
    def __init__(self, storage: Storage, checker: HealthChecker, urls: List[str]):
        self.storage = storage
        self.checker = checker
        self.urls = urls

    def run_cycle(self) -> List[Dict]:
        results = []

        for url in self.urls:
            previous = self.storage.get_last_check(url)
            current = self.checker.check(url)

            transition = self._detect_transition(previous, current)

            self.storage.insert_check(
                url=current.url,
                timestamp=current.timestamp,
                status=current.status,
                response_time=current.response_time,
                error=current.error,
            )

            if transition:
                self._alert_transition(url, transition)

            results.append(
                {
                    "result": current,
                    "transition": transition,
                }
            )

        return results

    def _detect_transition(
        self,
        previous: Optional[CheckResult],
        current: CheckResult,
    ) -> Optional[Dict]:
        if not previous:
            return None

        if previous.status != current.status:
            return {
                "from": previous.status,
                "to": current.status,
                "timestamp": current.timestamp,
            }

        return None

    def _alert_transition(self, url: str, transition: Dict) -> None:
        print(
            f"ALERT: {url} transitioned "
            f"{transition['from']} → {transition['to']}"
        )

    def get_report(self, url: str) -> Optional[Dict]:
        return self.storage.get_summary(url)

    def get_history(self, url: str, limit: int = 20) -> List[CheckResult]:
        return self.storage.get_history(url, limit=limit)
