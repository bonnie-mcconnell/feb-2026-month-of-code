from typing import List, Dict, Optional

from .checker import HealthChecker
from .storage import Storage


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
                url=current["url"],
                timestamp=current["timestamp"],
                status=current["status"],
                response_time=current["response_time"],
                error=current["error"],
            )

            if transition:
                self._alert_transition(url, transition)

            current["transition"] = transition
            results.append(current)

        return results

    def _detect_transition(
        self,
        previous: Optional[Dict],
        current: Dict,
    ) -> Optional[Dict]:
        if not previous:
            return None

        prev_status = previous["status"]
        curr_status = current["status"]

        if prev_status != curr_status:
            return {
                "from": prev_status,
                "to": curr_status,
                "timestamp": current["timestamp"],
            }

        return None

    def _alert_transition(self, url: str, transition: Dict) -> None:
        print(
            f"ALERT: {url} transitioned "
            f"{transition['from']} → {transition['to']}"
        )

    def get_report(self, url: str) -> Optional[Dict]:
        return self.storage.get_summary(url)

    def get_history(self, url: str, limit: int = 20) -> List[Dict]:
        return self.storage.get_history(url, limit=limit)
