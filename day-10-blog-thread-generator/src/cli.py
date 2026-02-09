from __future__ import annotations

import argparse
import sys
from typing import List

from loader import load_input
from preprocess import preprocess_text
from segment import segment_text
from thread_generator import generate_variant_1, generate_variant_2
from output_formatter import emit_output


VARIANT_MAP = {
    1: generate_variant_1,
    2: generate_variant_2,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blog-thread",
        description=(
            "Convert long-form blog content into structured social media threads. "
            "Deterministic, variant-based output."
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
        "--variant",
        type=str,
        default="1",
        help=(
            "Comma-separated list of variants to generate (e.g. 1,2). "
            "Available: 1=Conservative Sequential, 2=Heading-First Emphasis"
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text output",
    )

    parser.add_argument(
        "--out",
        help="Write output to a file instead of stdout (for multiple variants, a directory is recommended)",
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

    variant_ids: List[int] = []
    for v in args.variant.split(","):
        try:
            vid = int(v.strip())
            if vid not in VARIANT_MAP:
                raise ValueError()
            variant_ids.append(vid)
        except ValueError:
            print(f"Invalid variant id: {v}", file=sys.stderr)
            return 1

    # Generate all requested variants
    variants = []
    for vid in variant_ids:
        variant_func = VARIANT_MAP[vid]
        variant = variant_func(segments=segments, max_chars=args.max_chars)
        variants.append(variant)

    # Output all variants
    for i, variant in enumerate(variants, start=1):
        out_path = None
        if args.out:
            # if multiple variants, append variant number to file
            out_path = f"{args.out.rstrip('.json')}_variant{variant_ids[i-1]}.{'json' if args.json else 'txt'}"
        emit_output(variant, as_json=args.json, out_path=out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
