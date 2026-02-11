from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .log import record_decision
from .query import load_decisions, filter_by_actor, filter_by_tag
from .outcomes import Outcome, load_all as load_outcomes, append as append_outcome
from .storage import load_all as load_decisions_raw


DEFAULT_STORAGE_PATH = Path("data/decisions.json")
DEFAULT_OUTCOME_PATH = Path("data/outcomes.json")


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


def cmd_add_outcome(args: argparse.Namespace) -> None:
    decisions = load_decisions_raw(args.storage_path)
    if not any(d.decision_id == args.decision_id for d in decisions):
        raise SystemExit(f"No decision found with id {args.decision_id}")
    outcome = Outcome.create(
        decision_id=args.decision_id,
        outcome=args.outcome,
        notes=args.notes,
    )
    append_outcome(outcome, args.outcome_storage_path)
    print(f"Recorded outcome {outcome.outcome_id} for decision {outcome.decision_id}")


def cmd_list_outcomes(args: argparse.Namespace) -> None:
    outcomes = load_outcomes(args.outcome_storage_path)
    if args.decision_id:
        outcomes = [o for o in outcomes if o.decision_id == args.decision_id]

    if args.json:
        import json
        print(json.dumps([o.to_dict() for o in outcomes], indent=2))
        return

    for o in outcomes:
        print(f"{o.timestamp} | {o.decision_id} | {o.outcome} | {o.notes or ''}")


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

    add_outcome_cmd = subparsers.add_parser("add-outcome", help="Add an outcome to a decision")
    add_outcome_cmd.set_defaults(func=cmd_add_outcome)
    add_outcome_cmd.add_argument("--decision-id", required=True)
    add_outcome_cmd.add_argument("--outcome", required=True)
    add_outcome_cmd.add_argument("--notes")
    add_outcome_cmd.add_argument(
        "--outcome-storage-path",
        type=Path,
        default=DEFAULT_OUTCOME_PATH,
        help="Path to outcome log file",
    )

    list_outcomes_cmd = subparsers.add_parser("list-outcomes", help="List decision outcomes")
    list_outcomes_cmd.set_defaults(func=cmd_list_outcomes)
    list_outcomes_cmd.add_argument("--decision-id")
    list_outcomes_cmd.add_argument(
        "--outcome-storage-path",
        type=Path,
        default=DEFAULT_OUTCOME_PATH,
        help="Path to outcome log file",
    )
    list_outcomes_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()


