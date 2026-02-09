from typing import List

from .transcript_loader import TranscriptLine


def preprocess_lines(lines: List[TranscriptLine]) -> List[TranscriptLine]:
    """
    Light normalization pass over transcript lines.

    This step is intentionally conservative:
    - normalize whitespace
    - drop empty lines

    No semantic rewriting or inference is performed.
    """
    cleaned: List[TranscriptLine] = []

    for line in lines:
        text = " ".join(line.text.split())
        if not text:
            continue

        cleaned.append(
            TranscriptLine(
                index=line.index,
                text=text,
                start_sec=line.start_sec,
                end_sec=line.end_sec,
            )
        )

    return cleaned
