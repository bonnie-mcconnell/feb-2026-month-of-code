from dataclasses import dataclass
from typing import List, Optional
import re

from .segment import Segment
from .transcript_loader import TranscriptLine


# ---------- Key Ideas ----------

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
    "right",
)


def extract_key_ideas(segment: Segment) -> List[KeyIdea]:
    """
    Extract declarative key ideas from a transcript segment.

    Intentionally conservative: prefers false negatives over false positives.
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
    stripped = lowered_text.strip()
    return any(stripped.startswith(prefix) for prefix in NEGATIVE_PREFIXES)


def _classify_confidence(lowered_text: str) -> Optional[str]:
    if any(marker in lowered_text for marker in DECLARATIVE_MARKERS):
        return "high"

    if any(marker in lowered_text for marker in GENERALIZATION_MARKERS + EXPLANATORY_MARKERS):
        return "medium"

    return None


def _clean_text(text: str) -> str:
    return text.rstrip(".").strip()


def _stands_alone(text: str) -> bool:
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


# ---------- Action Items ----------

@dataclass
class ActionItem:
    text: str
    segment_id: int
    start_sec: Optional[int]


ACTION_TRIGGERS = [
    r"\byou should\b",
    r"\byou can\b",
    r"\bi recommend\b",
    r"\bi suggest\b",
    r"\btry\b",
    r"\bmake sure\b",
    r"\bstart by\b",
    r"\bthe next step is\b",
    r"\bwhat you want to do\b",
]

ACTION_VERBS = {
    "run",
    "write",
    "check",
    "test",
    "log",
    "measure",
    "compare",
    "remove",
    "add",
    "validate",
    "pause",
    "review",
    "refactor",
    "track",
    "monitor",
    "inspect",
}

FILLER_PREFIX = re.compile(
    r"^(so|basically|okay|now|then)\s+",
    re.IGNORECASE,
)


def extract_action_items(segments: List[Segment]) -> List[ActionItem]:
    """
    Extract explicit, listener-directed action items from transcript segments.
    """
    action_items: List[ActionItem] = []
    trigger_pattern = re.compile("|".join(ACTION_TRIGGERS), re.IGNORECASE)

    for segment in segments:
        for line in segment.lines:
            text = line.text.strip()

            if not trigger_pattern.search(text):
                continue

            if not _contains_action_verb(text):
                continue

            cleaned = _clean_action_text(text)
            if not cleaned:
                continue

            action_items.append(
                ActionItem(
                    text=cleaned,
                    segment_id=segment.segment_id,
                    start_sec=line.start_sec,
                )
            )

    return action_items


def _contains_action_verb(text: str) -> bool:
    tokens = re.findall(r"\b[a-z]+\b", text.lower())
    return any(token in ACTION_VERBS for token in tokens)


def _clean_action_text(text: str) -> str:
    cleaned = FILLER_PREFIX.sub("", text.strip())

    cleaned = re.sub(
        r"(,?\s+(right|okay|you know|kind of).*)$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned.strip()
