from __future__ import annotations

import argparse
import sys

from loader import load_input
from preprocess import preprocess_text
from segment import segment_text
from thread_generator import generate_variant_1
from output_formatter import emit_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blog-thread",
        description=(
            "Convert long-form blog content into a structured social media thread. "
            "This tool performs deterministic content structuring only."
        ),
    )

    parser.add_argument(
        "input_path",
        help="Path to a plain text or Markdown blog file",
    )

    parser.add_argument(
        "--max-chars",
        type=int,
        default=280,
        help="Maximum characters per post (default: 280)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text output",
    )

    parser.add_argument(
        "--out",
        help="Write output to a file instead of stdout",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_chars <= 0:
        print("Error: --max-chars must be a positive integer", file=sys.stderr)
        return 1

    try:
        raw_text, detected_format = load_input(args.input_path)
    except Exception as exc:
        print(f"Error loading input: {exc}", file=sys.stderr)
        return 1

    cleaned = preprocess_text(raw_text)
    segments = segment_text(cleaned)

    variant = generate_variant_1(
        segments=segments,
        max_chars=args.max_chars,
    )

    emit_output(
        variant,
        as_json=args.json,
        out_path=args.out,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
