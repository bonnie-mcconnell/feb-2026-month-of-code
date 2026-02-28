from typing import List
from .types import RequestObservation


def filter_window(
    observations: List[RequestObservation],
    *,
    window_start: int,
    window_end: int,
) -> List[RequestObservation]:
    return [
        o for o in observations
        if window_start <= o.timestamp <= window_end
    ]