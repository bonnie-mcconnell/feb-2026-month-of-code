from pathlib import Path

from ..parsing.text_extractor import extract_text_lines
from ..parsing.strategies.registry import StrategyRegistry
from ..domain.invoice import Invoice


def extract_invoice_from_pdf(pdf_path: Path) -> Invoice:
    lines = extract_text_lines(pdf_path)
    return extract_invoice_from_lines(lines)


def extract_invoice_from_lines(lines: list[str]) -> Invoice:
    registry = StrategyRegistry()
    strategy = registry.resolve(lines)
    return strategy.parse(lines)