from __future__ import annotations

from pathlib import Path
from typing import List

from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

from .errors import InvoiceParseError


def extract_text_lines(pdf_path: Path) -> List[str]:
    """
    Extracts text from a PDF and returns normalized lines.

    Deterministic behavior:
    - Preserves line order
    - Normalizes newline characters
    - Strips trailing whitespace
    - Removes leading/trailing empty lines
    """

    if not pdf_path.exists():
        raise InvoiceParseError(
            f"File not found: {pdf_path}",
            "PDF_READ_ERROR",
        )

    try:
        raw_text = extract_text(str(pdf_path))
    except PDFSyntaxError as e:
        raise InvoiceParseError(
            f"Invalid PDF format: {e}",
            "PDF_READ_ERROR",
        )
    except Exception as e:
        raise InvoiceParseError(
            f"Failed to read PDF: {e}",
            "PDF_READ_ERROR",
        )

    if not raw_text or not raw_text.strip():
        raise InvoiceParseError(
            "PDF contains no extractable text",
            "EMPTY_DOCUMENT",
        )

    # Normalize newlines
    raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [line.rstrip() for line in raw_text.split("\n")]

    # Remove leading/trailing blank lines deterministically
    lines = _strip_empty_edges(lines)

    if not lines:
        raise InvoiceParseError(
            "No usable content extracted from PDF",
            "EMPTY_DOCUMENT",
        )

    return lines


def _strip_empty_edges(lines: List[str]) -> List[str]:
    start = 0
    end = len(lines)

    while start < end and not lines[start].strip():
        start += 1

    while end > start and not lines[end - 1].strip():
        end -= 1

    return lines[start:end]