import json
import logging
import sys
import time
from typing import Any, Dict


class JsonLogger:
    def __init__(self, debug: bool = False):
        self.logger = logging.getLogger("cloud_backup")
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.handlers = [handler]

    def log(self, event: str, **fields: Any) -> None:
        payload: Dict[str, Any] = {
            "event": event,
            "timestamp": time.time(),
        }

        payload.update(fields)

        self.logger.info(json.dumps(payload, separators=(",", ":")))