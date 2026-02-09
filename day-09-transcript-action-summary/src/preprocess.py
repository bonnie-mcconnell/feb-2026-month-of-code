from typing import List

from src.transcript_loader import TranscriptLine


def preprocess_lines(lines: List[TranscriptLine]) -> List[TranscriptLine]:
    """
    Light normalization pass over transcript lines.

    This step is intentionally conservative:
    - normalize whitespace
    - drop empty lines

    No semantic rewriting or inference is performed.
    """
    cleaned: List[TranscriptLine] = []

    prev_line = None
    for line in lines:
        text = " ".join(line.text.split())
        if not text:
            continue

        if prev_line and prev_line.text.endswith(",") and text[0].islower():
            # merge with previous
            prev_line.text += " " + text
        else:
            if prev_line:
                cleaned.append(prev_line)
            prev_line = TranscriptLine(
                index=line.index,
                text=text,
                start_sec=line.start_sec,
                end_sec=line.end_sec,
                speaker=line.speaker
            )

    if prev_line:
        cleaned.append(prev_line)

    return cleaned

