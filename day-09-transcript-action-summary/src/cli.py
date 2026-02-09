import argparse
import sys

from .transcript_loader import load_transcript
from .preprocess import preprocess_lines
from .segment import segment_transcript
from .extract import extract_key_ideas, extract_action_items
from .format_output import format_as_text, format_as_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured key ideas and action items from transcripts"
    )

    parser.add_argument(
        "source",
        help="YouTube URL or path to transcript file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of human-readable text",
    )

    args = parser.parse_args()

    try:
        lines, has_timestamps = load_transcript(args.source)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    lines = preprocess_lines(lines)

    segments = segment_transcript(
        transcript_lines=lines,
        has_timestamps=has_timestamps,
    )

    key_ideas = []
    for segment in segments:
        key_ideas.extend(extract_key_ideas(segment))

    action_items = extract_action_items(segments)

    if args.json:
        output = format_as_json(
            key_ideas=key_ideas,
            action_items=action_items,
            segments=segments,
            source=args.source,
        )
    else:
        output = format_as_text(
            key_ideas=key_ideas,
            action_items=action_items,
        )

    print(output)
