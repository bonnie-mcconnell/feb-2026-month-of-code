from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditRecord:
    message_id: str
    timestamp: datetime
    event: str
    metadata: dict