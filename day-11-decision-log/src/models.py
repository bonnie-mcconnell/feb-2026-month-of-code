from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import json


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _validate_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_json_serializable(value: Any, field_name: str) -> None:
    try:
        json.dumps(value)
    except TypeError:
        raise ValueError(f"{field_name} must be JSON-serializable")


@dataclass(frozen=True)
class Decision:
    decision_id: str
    timestamp: str
    actor: str
    title: str
    description: str
    context: str
    inputs: Dict[str, Any]

    options_considered: Optional[List[str]] = None
    tradeoffs: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def create(
        *,
        actor: str,
        title: str,
        description: str,
        context: str,
        inputs: Dict[str, Any],
        options_considered: Optional[List[str]] = None,
        tradeoffs: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> "Decision":
        _validate_non_empty(actor, "actor")
        _validate_non_empty(title, "title")
        _validate_non_empty(description, "description")
        _validate_non_empty(context, "context")

        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a dictionary")
        _validate_json_serializable(inputs, "inputs")

        if options_considered is not None:
            if not all(isinstance(opt, str) and opt.strip() for opt in options_considered):
                raise ValueError("options_considered must be a list of non-empty strings")

        if tradeoffs is not None:
            _validate_non_empty(tradeoffs, "tradeoffs")

        tag_list = tags or []
        if not all(isinstance(tag, str) and tag.strip() for tag in tag_list):
            raise ValueError("tags must be a list of non-empty strings")

        return Decision(
            decision_id=str(uuid.uuid4()),
            timestamp=_utc_now_iso(),
            actor=actor,
            title=title,
            description=description,
            context=context,
            inputs=inputs,
            options_considered=options_considered,
            tradeoffs=tradeoffs,
            tags=tag_list,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "inputs": self.inputs,
            "options_considered": self.options_considered,
            "tradeoffs": self.tradeoffs,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Decision":
        return Decision(**data)
