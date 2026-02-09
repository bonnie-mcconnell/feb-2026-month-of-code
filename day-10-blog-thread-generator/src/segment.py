from dataclasses import dataclass
from typing import List, Optional
import re


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
_UNORDERED_LIST_RE = re.compile(r"^[-*]\s+(.*)")
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s+(.*)")


@dataclass
class Segment:
    id: int
    type: str  # heading | paragraph | list_item
    level: Optional[int]
    text: str
    source_order: int
    parent_heading_id: Optional[int]
    char_count: int
    is_split: bool = False
    split_index: Optional[int] = None


def segment_text(preprocessed_text: str) -> List[Segment]:
    segments: List[Segment] = []

    current_paragraph: List[str] = []
    current_parent_heading_id: Optional[int] = None
    segment_id = 1
    source_order = 1

    def flush_paragraph():
        nonlocal segment_id, source_order, current_paragraph
        if not current_paragraph:
            return

        text = " ".join(current_paragraph)
        segments.append(
            Segment(
                id=segment_id,
                type="paragraph",
                level=None,
                text=text,
                source_order=source_order,
                parent_heading_id=current_parent_heading_id,
                char_count=len(text),
            )
        )
        segment_id += 1
        source_order += 1
        current_paragraph = []

    lines = preprocessed_text.split("\n")

    for line in lines:
        if not line.strip():
            flush_paragraph()
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            text = heading_match.group(2)

            segment = Segment(
                id=segment_id,
                type="heading",
                level=level,
                text=text,
                source_order=source_order,
                parent_heading_id=None,
                char_count=len(text),
            )
            segments.append(segment)

            current_parent_heading_id = segment.id
            segment_id += 1
            source_order += 1
            continue

        unordered_match = _UNORDERED_LIST_RE.match(line)
        if unordered_match:
            flush_paragraph()
            item_text = unordered_match.group(1)

            segments.append(
                Segment(
                    id=segment_id,
                    type="list_item",
                    level=None,
                    text=item_text,
                    source_order=source_order,
                    parent_heading_id=current_parent_heading_id,
                    char_count=len(item_text),
                )
            )
            segment_id += 1
            source_order += 1
            continue

        ordered_match = _ORDERED_LIST_RE.match(line)
        if ordered_match:
            flush_paragraph()
            item_text = ordered_match.group(1)
            segments.append(
                Segment(
                    id=segment_id,
                    type="list_item",
                    level=None,
                    text=item_text,
                    source_order=source_order,
                    parent_heading_id=current_parent_heading_id,
                    char_count=len(item_text),
                )
            )
            segment_id += 1
            source_order += 1
            continue

        # Otherwise, part of a paragraph
        current_paragraph.append(line)

    flush_paragraph()
    return segments
