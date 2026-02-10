from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Decision
from .storage import append


def record_decision(
    *,
    actor: str,
    title: str,
    description: str,
    context: str,
    inputs: Dict[str, Any],
    storage_path: Path,
    options_considered: Optional[List[str]] = None,
    tradeoffs: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Decision:
    decision = Decision.create(
        actor=actor,
        title=title,
        description=description,
        context=context,
        inputs=inputs,
        options_considered=options_considered,
        tradeoffs=tradeoffs,
        tags=tags,
    )

    append(decision, storage_path)
    return decision
