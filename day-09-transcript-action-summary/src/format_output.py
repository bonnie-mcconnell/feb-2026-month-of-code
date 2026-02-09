from typing import List, Dict, Any, Optional
import json

from src.segment import Segment
from src.extract import KeyIdea, ActionItem


def format_as_text(
    *,
    key_ideas: List[KeyIdea],
    action_items: List[ActionItem],
    segments: Optional[List[Segment]] = None,
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
        lines.append("")

    if segments:
        lines.append("SEGMENTS")
        lines.append("-" * 8)
        for seg in segments:
            seg_range = ""
            if seg.start_sec is not None and seg.end_sec is not None:
                seg_range = f" ({seg.start_sec}-{seg.end_sec}s)"
            lines.append(f"[Segment {seg.segment_id}]{seg_range}")
        lines.append("")

    return "\n".join(lines)


def format_as_markdown(
    *,
    key_ideas: List[KeyIdea],
    action_items: List[ActionItem],
    segments: Optional[List[Segment]],
    source: str,
) -> str:
    lines: List[str] = []

    lines.append(f"# Transcript Summary")
    lines.append(f"**Source:** {source}")
    lines.append("")

    if key_ideas:
        lines.append("## Key Ideas")
        for idea in key_ideas:
            icon = "🔴" if idea.confidence == "high" else "🟡" if idea.confidence == "medium" else "⚪"
            lines.append(f"- {icon} **{idea.confidence.capitalize()}** — {idea.text}")
        lines.append("")

    if action_items:
        lines.append("## Action Items")
        for item in action_items:
            ts = f" ({item.start_sec}s)" if item.start_sec else ""
            lines.append(f"- {item.text}{ts}")
        lines.append("")

    if segments:
        lines.append("## Segments")
        for seg in segments:
            header = f"### Segment {seg.segment_id}"
            if seg.start_sec is not None and seg.end_sec is not None:
                header += f" ({seg.start_sec}-{seg.end_sec}s)"
            lines.append(header)
            for line in seg.lines:
                speaker = f"{line.speaker}: " if line.speaker else ""
                lines.append(f"- {speaker}{line.text}")
            lines.append("")

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
                "score": round(idea.score, 2),
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
