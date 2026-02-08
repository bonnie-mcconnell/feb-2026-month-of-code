from dataclasses import dataclass
from typing import List

from .segment import Segment


@dataclass
class KeyIdea:
    text: str
    confidence: str  # "high" | "medium"


DECLARATIVE_MARKERS = (
    " is ",
    " are ",
    " means ",
    " happens ",
)

GENERALIZATION_MARKERS = (
    " often ",
    " usually ",
    " in practice ",
    " most ",
)

EXPLANATORY_MARKERS = (
    " because ",
    " which means ",
    " so ",
)

NEGATIVE_PREFIXES = (
    "for example",
    "let me",
    "i want to",
    "you can see",
    "right?",
)


def extract_key_ideas(segment: Segment) -> List[KeyIdea]:
    """
    Extract declarative key ideas from a transcript segment.

    This function uses conservative heuristics and prefers
    false negatives over false positives.
    """
    ideas: List[KeyIdea] = []

    for line in segment.lines:
        text = line.text.strip()
        lowered = f" {text.lower()} "

        if _should_ignore(lowered):
            continue

        confidence = _classify_confidence(lowered)
        if confidence is None:
            continue

        cleaned = _clean_text(text)
        if not _stands_alone(cleaned):
            continue

        ideas.append(
            KeyIdea(
                text=cleaned,
                confidence=confidence,
            )
        )

    return _deduplicate(ideas)


def _should_ignore(lowered_text: str) -> bool:
    return any(lowered_text.strip().startswith(prefix) for prefix in NEGATIVE_PREFIXES)


def _classify_confidence(lowered_text: str):
    if any(marker in lowered_text for marker in DECLARATIVE_MARKERS):
        return "high"

    if any(marker in lowered_text for marker in GENERALIZATION_MARKERS + EXPLANATORY_MARKERS):
        return "medium"

    return None


def _clean_text(text: str) -> str:
    # Minimal cleanup only; no rewriting
    return text.rstrip(".").strip()


def _stands_alone(text: str) -> bool:
    # Reject very short or fragment-like statements
    return len(text.split()) >= 6


def _deduplicate(ideas: List[KeyIdea]) -> List[KeyIdea]:
    seen = set()
    unique: List[KeyIdea] = []

    for idea in ideas:
        key = idea.text.lower()
        if key not in seen:
            seen.add(key)
            unique.append(idea)

    return unique
