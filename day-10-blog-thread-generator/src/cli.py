import argparse
import sys

from loader import load_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert blog content into structured social media thread variants. "
            "This tool performs deterministic content structuring only."
        )
    )

    parser.add_argument(
        "input_path",
        help="Path to a plain text or Markdown blog file",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--max-chars",
        type=int,
        default=280,
        help="Maximum characters per social post (default: 280)",
    )

    parser.add_argument(
        "--variants",
        default=None,
        help="Comma-separated list of thread variants to generate (e.g. 1,2,3)",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any warnings are produced during processing",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.max_chars <= 0:
        print("Error: --max-chars must be a positive integer", file=sys.stderr)
        sys.exit(1)

    try:
        raw_text, detected_format = load_input(args.input_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Placeholder for future pipeline stages
    if args.debug:
        print("Debug:")
        print(f"  Detected format: {detected_format}")
        print(f"  Input length: {len(raw_text)} characters")

    print("Input loaded successfully.")
    print("Thread generation not yet implemented.")


if __name__ == "__main__":
    main()
