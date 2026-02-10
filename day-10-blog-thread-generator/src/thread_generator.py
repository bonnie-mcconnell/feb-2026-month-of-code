from dataclasses import dataclass
from typing import List

from .segment import Segment



@dataclass
class ThreadPost:
    text: str
    segment_ids: List[int]
    char_count: int


@dataclass
class ThreadVariant:
    name: str
    posts: List[ThreadPost]
    warnings: List[str]


# -------------------------
# Variant 1
# -------------------------

def generate_variant_1(
    segments: List[Segment],
    max_chars: int,
) -> ThreadVariant:
    posts: List[ThreadPost] = []
    warnings: List[str] = []

    current_parts: List[str] = []
    current_segment_ids: List[int] = []
    current_len = 0
    current_parent_heading_id: int | None = None

    def flush_post() -> None:
        nonlocal current_parts, current_segment_ids, current_len

        if not current_parts:
            return

        text = " ".join(current_parts).strip()

        posts.append(
            ThreadPost(
                text=text,
                segment_ids=current_segment_ids.copy(),
                char_count=len(text),
            )
        )

        current_parts = []
        current_segment_ids = []
        current_len = 0

    for segment in segments:
        # Enforce hard heading boundary
        if current_parent_heading_id is None:
            current_parent_heading_id = segment.parent_heading_id
        elif segment.parent_heading_id != current_parent_heading_id:
            flush_post()
            current_parent_heading_id = segment.parent_heading_id

        if segment.char_count > max_chars:
            warnings.append(
                f"Segment {segment.id} exceeds max_chars and was split"
            )
            flush_post()
            _split_and_emit_segment(segment, max_chars, posts, warnings)
            continue

        projected = current_len + (1 if current_parts else 0) + segment.char_count
        if projected > max_chars:
            flush_post()

        current_parts.append(segment.text)
        current_segment_ids.append(segment.id)
        current_len += (1 if current_len else 0) + segment.char_count

    flush_post()

    return ThreadVariant(
        name="Variant 1: Conservative Sequential",
        posts=posts,
        warnings=warnings,
    )


# -------------------------
# Variant 2
# -------------------------

def generate_variant_2(
    segments: List[Segment],
    max_chars: int,
) -> ThreadVariant:
    """
    Variant 2: Heading-First Emphasis

    Each top-level heading (level 1) starts a new post.
    The heading text is prepended once to the first segment under it.
    """

    posts: List[ThreadPost] = []
    warnings: List[str] = []

    current_parts: List[str] = []
    current_segment_ids: List[int] = []
    current_len = 0
    pending_heading: str | None = None

    def flush_post() -> None:
        nonlocal current_parts, current_segment_ids, current_len

        if not current_parts:
            return

        text = " ".join(current_parts).strip()

        posts.append(
            ThreadPost(
                text=text,
                segment_ids=current_segment_ids.copy(),
                char_count=len(text),
            )
        )

        current_parts = []
        current_segment_ids = []
        current_len = 0

    for segment in segments:
        if segment.type == "heading" and segment.level == 1:
            flush_post()
            pending_heading = segment.text
            continue

        text = segment.text
        if pending_heading:
            text = f"{pending_heading}: {text}"
            pending_heading = None

        if segment.char_count > max_chars:
            warnings.append(
                f"Segment {segment.id} exceeds max_chars and was split"
            )
            flush_post()
            _split_and_emit_segment(segment, max_chars, posts, warnings)
            continue

        projected = current_len + (1 if current_parts else 0) + len(text)
        if projected > max_chars:
            flush_post()

        current_parts.append(text)
        current_segment_ids.append(segment.id)
        current_len = projected

    flush_post()

    return ThreadVariant(
        name="Variant 2: Heading-First Emphasis",
        posts=posts,
        warnings=warnings,
    )


# -------------------------
# Splitting helpers
# -------------------------

def _split_and_emit_segment(
    segment: Segment,
    max_chars: int,
    posts: List[ThreadPost],
    warnings: List[str],
) -> None:
    sentences = _split_into_sentences(segment.text)

    buffer: List[str] = []
    buffer_len = 0

    def flush_buffer():
        nonlocal buffer, buffer_len
        if not buffer:
            return
        text = " ".join(buffer).strip()
        posts.append(
            ThreadPost(
                text=text,
                segment_ids=[segment.id],
                char_count=len(text),
            )
        )
        buffer = []
        buffer_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if sentence_len > max_chars:
            warnings.append(
                f"Sentence in segment {segment.id} exceeds max_chars; hard split applied"
            )
            flush_buffer()
            for i in range(0, sentence_len, max_chars):
                chunk = sentence[i : i + max_chars]
                posts.append(
                    ThreadPost(
                        text=chunk,
                        segment_ids=[segment.id],
                        char_count=len(chunk),
                    )
                )
            continue

        projected = buffer_len + (1 if buffer else 0) + sentence_len
        if projected > max_chars:
            flush_buffer()

        buffer.append(sentence)
        buffer_len = (
            buffer_len + (1 if buffer_len else 0) + sentence_len
        )

    flush_buffer()


def _split_into_sentences(text: str) -> List[str]:
    sentences: List[str] = []
    current = ""

    for char in text:
        current += char
        if char in ".!?":
            sentences.append(current.strip())
            current = ""

    if current.strip():
        sentences.append(current.strip())

    return sentences
