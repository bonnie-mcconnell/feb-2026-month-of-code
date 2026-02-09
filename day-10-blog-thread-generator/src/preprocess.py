import re
import unicodedata


_BLANK_LINE_RE = re.compile(r"\n{3,}")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")


def preprocess_text(raw_text: str) -> str:
    """
    Normalize raw blog text to make downstream segmentation and
    character counting deterministic.

    This function is intentionally conservative: it removes
    formatting noise without interpreting or restructuring content.
    """
    if not raw_text:
        return raw_text

    # Normalize Unicode to avoid visually identical characters
    # counting differently across platforms.
    text = unicodedata.normalize("NFKC", raw_text)

    # Strip trailing whitespace on each line. This prevents invisible
    # characters from affecting length-based logic later.
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Collapse excessive blank lines into a single blank line.
    # Paragraph boundaries are preserved.
    text = _BLANK_LINE_RE.sub("\n\n", text)

    # Collapse repeated spaces and tabs inside lines.
    # This avoids accidental overflows without altering meaning.
    text = _MULTI_SPACE_RE.sub(" ", text)

    return text
