from __future__ import annotations

import argparse
import sys
import os
import json
from typing import List

from .loader import load_input
from .preprocess import preprocess_text
from .segment import segment_text
from .thread_generator import generate_variant_1, generate_variant_2
from .output_formatter import emit_output, format_json_thread


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
        help="Emit machine-readable JSON (single-line, pipe-safe)",
    )
    parser.add_argument(
        "--out",
        help=(
            "Write output to a file instead of stdout. "
            "For multiple variants, a directory or filename prefix is recommended."
        ),
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_chars <= 0:
        print("Error: --max-chars must be a positive integer", file=sys.stderr)
        return 1

    try:
        raw_text, _detected_format = load_input(args.input_path)
    except UnicodeDecodeError:
        print(f"Error loading input: File must be UTF-8 encoded: {args.input_path}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error loading input: {exc}", file=sys.stderr)
        return 1


    cleaned = preprocess_text(raw_text)
    segments = segment_text(cleaned)

    # Parse variants
    variant_ids: List[int] = []
    for v in args.variant.split(","):
        try:
            vid = int(v.strip())
            if vid not in VARIANT_MAP:
                raise ValueError
            variant_ids.append(vid)
        except ValueError:
            print(f"Invalid variant id: {v}. Available: {', '.join(map(str, VARIANT_MAP.keys()))}", file=sys.stderr)
            return 1

    # Generate variants
    variants = []
    for vid in variant_ids:
        variant_func = VARIANT_MAP[vid]
        variant = variant_func(segments=segments, max_chars=args.max_chars)
        variants.append(variant)

    # -------------------------
    # JSON output (machine-safe)
    # -------------------------
    if args.json:
        combined = {
            f"Variant {vid}": format_json_thread(variant)
            for vid, variant in zip(variant_ids, variants)
        }

        # IMPORTANT: single-line JSON (tests + pipe safety)
        payload = json.dumps(combined, ensure_ascii=False)

        if args.out:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(payload)
        else:
            print(payload)

        return 0

    # -------------------------
    # Text output
    # -------------------------
    for i, variant in enumerate(variants):
        out_path = None
        if args.out:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

            if len(variants) > 1:
                base, ext = os.path.splitext(args.out)
                ext = ext or ".txt"
                out_path = f"{base}_variant{variant_ids[i]}{ext}"
            else:
                out_path = args.out

        emit_output(
            variant,
            as_json=False,
            out_path=out_path,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
