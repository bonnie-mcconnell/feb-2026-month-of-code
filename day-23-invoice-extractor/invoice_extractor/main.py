import argparse
import json
import sys
from pathlib import Path

from .services.extractor_services import extract_invoice_from_pdf
from .domain.validation import validate_invoice, InvoiceValidationError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured data from invoice PDFs"
    )
    parser.add_argument("pdf_path", type=Path, help="Path to the invoice PDF")
    parser.add_argument("--json", action="store_true", help="Output invoice as JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Validate invoice and fail on inconsistencies",
    )

    args = parser.parse_args()

    try:
        invoice = extract_invoice_from_pdf(args.pdf_path)

        if args.strict:
            validate_invoice(invoice)

        if args.json:
            print(json.dumps(invoice.to_dict(), indent=2))
        else:
            print(invoice)

    except InvoiceValidationError as e:
        print(f"Validation Error [{e.code}]: {e}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print(f"File not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Failed to extract invoice: {e}", file=sys.stderr)
        sys.exit(3)