import argparse
import json
from pathlib import Path

from ..services.extractor_services import extract_invoice_from_pdf
from ..domain.validation import validate_invoice


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured data from invoice PDFs"
    )
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    invoice = extract_invoice_from_pdf(args.pdf_path)

    validate_invoice(invoice)

    if args.json:
        print(json.dumps(invoice.to_dict(), indent=2))
    else:
        print(invoice)