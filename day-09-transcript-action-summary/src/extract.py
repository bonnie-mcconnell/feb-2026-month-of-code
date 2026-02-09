from dataclasses import dataclass
from typing import List, Optional
import re

from src.segment import Segment
from src.sentence_splitter import split_sentences


# ---------- Key Ideas ----------

@dataclass
class KeyIdea:
    text: str
    confidence: str  # "high" | "medium" | "low"
    score: float


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


def confidence_score(matches: int) -> float:
    return min(1.0, 0.3 + matches * 0.25)


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def extract_key_ideas(segment: Segment) -> List[KeyIdea]:
    """
    Extract declarative key ideas from a transcript segment.
    Conservative by design.
    """
    ideas: List[KeyIdea] = []

    for line in segment.lines:
        for sentence in split_sentences(line.text):
            lowered = f" {sentence.lower()} "

            if _should_ignore(lowered):
                continue

            classified = _classify_confidence(lowered)
            if classified is None:
                continue

            label, score = classified

            cleaned = _clean_text(sentence)
            if not _stands_alone(cleaned):
                continue

            ideas.append(
                KeyIdea(
                    text=cleaned,
                    confidence=label,
                    score=score,
                )
            )

    return _deduplicate(ideas)


def _should_ignore(lowered_text: str) -> bool:
    stripped = lowered_text.strip()
    return any(stripped.startswith(prefix) for prefix in NEGATIVE_PREFIXES)


def _classify_confidence(lowered_text: str) -> Optional[tuple[str, float]]:
    matches = 0

    for marker in DECLARATIVE_MARKERS:
        if marker in lowered_text:
            matches += 2

    for marker in GENERALIZATION_MARKERS + EXPLANATORY_MARKERS:
        if marker in lowered_text:
            matches += 1

    if matches == 0:
        return None

    score = confidence_score(matches)
    label = confidence_label(score)

    return label, score



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
    action_items: List[ActionItem] = []
    trigger_pattern = re.compile("|".join(ACTION_TRIGGERS), re.IGNORECASE)

    for segment in segments:
        for line in segment.lines:
            for sentence in split_sentences(line.text):
                if not trigger_pattern.search(sentence):
                    continue

                if not _contains_action_verb(sentence):
                    continue

                cleaned = _clean_action_text(sentence)
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
