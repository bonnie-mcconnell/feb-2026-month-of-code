import argparse
import sys

from src.transcript_loader import load_transcript
from src.preprocess import preprocess_lines
from src.segment import segment_transcript
from src.extract import extract_key_ideas, extract_action_items
from src.format_output import (
    format_as_text,
    format_as_json,
    format_as_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured key ideas and action items from transcripts"
    )

    parser.add_argument(
        "source",
        help="YouTube URL or path to transcript file",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "md"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--segments",
        action="store_true",
        help="Include per-segment breakdown in output",
    )

    parser.add_argument(
        "--out",
        help="Write output to a file instead of stdout",
    )


    args = parser.parse_args()

    # -------- Load transcript --------
    try:
        lines, has_timestamps = load_transcript(args.source)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if not lines:
        print("ERROR: Transcript is empty", file=sys.stderr)
        sys.exit(1)

    # -------- Preprocess --------
    lines = preprocess_lines(lines)

    # -------- Segment --------
    segments = segment_transcript(
        transcript_lines=lines,
        has_timestamps=has_timestamps,
    )

    # -------- Extract --------
    key_ideas = [idea for segment in segments for idea in extract_key_ideas(segment)]

    action_items = extract_action_items(segments, key_ideas)

    # -------- Format --------
    if args.format == "json":
        output = format_as_json(
            key_ideas=key_ideas,
            action_items=action_items,
            segments=segments,
            source=args.source,
        )
    elif args.format == "md":
        output = format_as_markdown(
            key_ideas=key_ideas,
            action_items=action_items,
            segments=segments if args.segments else None,
            source=args.source,
        )
    else:
        output = format_as_text(
            key_ideas=key_ideas,
            action_items=action_items,
            segments=segments if args.segments else None,
        )

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(output)
                f.write("\n")
        except OSError as exc:
            print(f"ERROR: Failed to write output file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)
        

if __name__ == "__main__":
    main()
