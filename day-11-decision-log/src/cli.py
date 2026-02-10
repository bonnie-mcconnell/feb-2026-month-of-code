from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .log import record_decision
from .query import load_decisions, filter_by_actor, filter_by_tag


DEFAULT_STORAGE_PATH = Path("data/decisions.json")


def _parse_inputs(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON for inputs: {e}") from e


def cmd_add(args: argparse.Namespace) -> None:
    decision = record_decision(
        actor=args.actor,
        title=args.title,
        description=args.description,
        context=args.context,
        inputs=_parse_inputs(args.inputs),
        options_considered=args.options,
        tradeoffs=args.tradeoffs,
        tags=args.tags,
        storage_path=args.storage_path,
    )

    print(f"Recorded decision {decision.decision_id}")


def cmd_list(args: argparse.Namespace) -> None:
    decisions = load_decisions(args.storage_path)

    if args.actor:
        decisions = filter_by_actor(decisions, args.actor)
    if args.tag:
        decisions = filter_by_tag(decisions, args.tag)

    for d in decisions:
        print(f"{d.timestamp} | {d.actor} | {d.title}")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Decision log / audit trail")

    parser.add_argument(
        "--storage-path",
        type=Path,
        default=DEFAULT_STORAGE_PATH,
        help="Path to decision log file",
    )

    subparsers = parser.add_subparsers(required=True)

    add = subparsers.add_parser("add", help="Record a new decision")
    add.set_defaults(func=cmd_add)

    add.add_argument("--actor", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--description", required=True)
    add.add_argument("--context", required=True)
    add.add_argument(
        "--inputs",
        required=True,
        help="JSON string of inputs considered",
    )
    add.add_argument("--options", nargs="*")
    add.add_argument("--tradeoffs")
    add.add_argument("--tags", nargs="*")

    list_cmd = subparsers.add_parser("list", help="List recorded decisions")
    list_cmd.set_defaults(func=cmd_list)

    list_cmd.add_argument("--actor")
    list_cmd.add_argument("--tag")

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
