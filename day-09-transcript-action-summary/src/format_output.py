from typing import List, Dict, Any, Optional
import json

from .segment import Segment
from .extract import KeyIdea, ActionItem


def format_as_text(
    *,
    key_ideas: List[KeyIdea],
    action_items: List[ActionItem],
) -> str:
    lines: List[str] = []

    if key_ideas:
        lines.append("KEY IDEAS")
        lines.append("-" * 9)

        for idea in key_ideas:
            lines.append(f"[{idea.confidence.upper()}] {idea.text}")

        lines.append("")

    if action_items:
        lines.append("ACTION ITEMS")
        lines.append("-" * 12)

        for item in action_items:
            ts = f" @ {item.start_sec}s" if item.start_sec is not None else ""
            lines.append(f"- {item.text}{ts}")

    return "\n".join(lines)


def format_as_json(
    *,
    key_ideas: List[KeyIdea],
    action_items: List[ActionItem],
    segments: List[Segment],
    source: str,
) -> str:
    payload: Dict[str, Any] = {
        "source": source,
        "segments": len(segments),
        "key_ideas": [
            {
                "text": idea.text,
                "confidence": idea.confidence,
            }
            for idea in key_ideas
        ],
        "action_items": [
            {
                "segment_id": item.segment_id,
                "start_sec": item.start_sec,
                "text": item.text,
            }
            for item in action_items
        ],
    }

    return json.dumps(payload, indent=2)
