import pytest
from pathlib import Path

from invoice_extractor.parsing.text_extractor import extract_text_lines
from invoice_extractor.parsing.errors import InvoiceParseError


def test_file_not_found():
    with pytest.raises(InvoiceParseError) as exc:
        extract_text_lines(Path("nonexistent.pdf"))

    assert exc.value.code == "PDF_READ_ERROR"