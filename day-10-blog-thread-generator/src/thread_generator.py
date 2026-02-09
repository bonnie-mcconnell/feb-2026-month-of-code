from typing import List, Tuple
from dataclasses import dataclass

from segment import Segment


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


def generate_variant_1(
    segments: List[Segment],
    max_chars: int,
) -> ThreadVariant:
    posts: List[ThreadPost] = []
    warnings: List[str] = []

    current_text_parts: List[str] = []
    current_segment_ids: List[int] = []
    current_char_count = 0
    current_parent_heading_id = None

    def flush_post():
        nonlocal current_text_parts, current_segment_ids, current_char_count
        if not current_text_parts:
            return

        text = " ".join(current_text_parts)
        posts.append(
            ThreadPost(
                text=text,
                segment_ids=current_segment_ids.copy(),
                char_count=len(text),
            )
        )
        current_text_parts = []
        current_segment_ids = []
        current_char_count = 0

    for segment in segments:
        # Enforce heading boundary packing
        if (
            current_parent_heading_id is not None
            and segment.parent_heading_id != current_parent_heading_id
        ):
            flush_post()

        segment_text = segment.text

        if segment.char_count > max_chars:
            warnings.append(
                f"Segment {segment.id} exceeds max_chars and was split"
            )
            flush_post()
            _split_and_emit_segment(
                segment,
                max_chars,
                posts,
                warnings,
            )
            current_parent_heading_id = segment.parent_heading_id
            continue

        projected_len = (
            current_char_count
            + (1 if current_text_parts else 0)
            + segment.char_count
        )

        if projected_len > max_chars:
            flush_post()

        current_text_parts.append(segment_text)
        current_segment_ids.append(segment.id)
        current_char_count = (
            current_char_count
            + (1 if current_char_count else 0)
            + segment.char_count
        )
        current_parent_heading_id = segment.parent_heading_id

    flush_post()

    return ThreadVariant(
        name="Variant 1: Conservative Sequential",
        posts=posts,
        warnings=warnings,
    )


def generate_variant_2(
    segments: list[Segment],
    max_chars: int,
) -> ThreadVariant:
    """
    Variant 2: Heading-First Emphasis
    Each top-level heading (level 1) starts a new post. Heading text is prepended
    to the first segment under it. Segments under the same heading may span multiple posts
    if max_chars is exceeded. Deterministic and warnings preserved.
    """
    posts: list[ThreadPost] = []
    warnings: list[str] = []

    current_text_parts: list[str] = []
    current_segment_ids: list[int] = []
    current_char_count = 0
    current_heading_id: int | None = None
    heading_text: str | None = None

    def flush_post():
        nonlocal current_text_parts, current_segment_ids, current_char_count
        if not current_text_parts:
            return
        text = " ".join(current_text_parts)
        posts.append(
            ThreadPost(
                text=text,
                segment_ids=current_segment_ids.copy(),
                char_count=len(text),
            )
        )
        current_text_parts = []
        current_segment_ids = []
        current_char_count = 0

    for segment in segments:
        # Check if this is a top-level heading
        if segment.type == "heading" and segment.level == 1:
            flush_post()
            heading_text = segment.text
            current_heading_id = segment.id
            continue

        segment_text = segment.text
        if heading_text:
            segment_text = f"{heading_text}: {segment_text}"
            heading_text = None  # prepend only once

        if segment.char_count > max_chars:
            warnings.append(f"Segment {segment.id} exceeds max_chars and was split")
            flush_post()
            _split_and_emit_segment(segment, max_chars, posts, warnings)
            current_heading_id = segment.parent_heading_id
            continue

        projected_len = current_char_count + (1 if current_text_parts else 0) + len(segment_text)
        if projected_len > max_chars:
            flush_post()

        current_text_parts.append(segment_text)
        current_segment_ids.append(segment.id)
        current_char_count = projected_len

    flush_post()

    return ThreadVariant(
        name="Variant 2: Heading-First Emphasis",
        posts=posts,
        warnings=warnings,
    )


def _split_and_emit_segment(
    segment: Segment,
    max_chars: int,
    posts: List[ThreadPost],
    warnings: List[str],
) -> None:
    text = segment.text
    sentences = _split_into_sentences(text)

    buffer: List[str] = []
    buffer_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        if sentence_len > max_chars:
            warnings.append(
                f"Sentence in segment {segment.id} exceeds max_chars; hard split applied"
            )
            for i in range(0, sentence_len, max_chars):
                chunk = sentence[i : i + max_chars]
                posts.append(
                    ThreadPost(
                        text=chunk,
                        segment_ids=[segment.id],
                        char_count=len(chunk),
                    )
                )
            buffer = []
            buffer_len = 0
            continue

        projected = buffer_len + (1 if buffer else 0) + sentence_len
        if projected > max_chars:
            posts.append(
                ThreadPost(
                    text=" ".join(buffer),
                    segment_ids=[segment.id],
                    char_count=len(" ".join(buffer)),
                )
            )
            buffer = [sentence]
            buffer_len = sentence_len
        else:
            buffer.append(sentence)
            buffer_len = projected

    if buffer:
        posts.append(
            ThreadPost(
                text=" ".join(buffer),
                segment_ids=[segment.id],
                char_count=len(" ".join(buffer)),
            )
        )


def _split_into_sentences(text: str) -> List[str]:
    # Conservative sentence splitter
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
