import pytest
from pathlib import Path
from invoice_extractor.parsing.text_extractor import extract_text_lines
from invoice_extractor.parsing.errors import InvoiceParseError


def test_text_extractor_file_not_found() -> None:
    with pytest.raises(InvoiceParseError):
        extract_text_lines(Path("does_not_exist.pdf"))


def test_text_extractor_empty_file(tmp_path) -> None:
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_text("")

    with pytest.raises(InvoiceParseError):
        extract_text_lines(empty_file)


def test_text_extractor_invalid_type() -> None:
    from invoice_extractor.parsing.text_extractor import extract_text_lines
    import pytest

    with pytest.raises(Exception): 
        extract_text_lines(123)  # type: ignore[arg-type]