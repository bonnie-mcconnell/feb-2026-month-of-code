import re

SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [s.strip() for s in SENTENCE_END.split(text) if s.strip()]
