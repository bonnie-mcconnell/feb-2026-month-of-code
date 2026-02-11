from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .log import record_decision
from .query import (
    load_decisions,
    filter_by_actor,
    filter_by_tag,
    filter_by_time_range,
)
from .outcomes import Outcome, load_all as load_outcomes, append as append_outcome
from .storage import load_all as load_decisions_raw
from .metrics import (
    count_by_actor,
    count_by_tag,
    decision_count,
    outcome_count,
)
from .export import export_decisions_csv



DEFAULT_STORAGE_PATH = Path("data/decisions.json")
DEFAULT_OUTCOME_PATH = Path("data/outcomes.json")


def _load_inputs(args: argparse.Namespace) -> dict:
    if args.inputs and args.inputs.startswith("@"):
        path = Path(args.inputs[1:])
        try:
            return json.loads(path.read_text())
        except FileNotFoundError:
            raise SystemExit(f"Inputs file not found: {path}")
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON in inputs file: {e}") from e

    if args.inputs_file:
        try:
            return json.loads(Path(args.inputs_file).read_text())
        except FileNotFoundError:
            raise SystemExit(f"Inputs file not found: {args.inputs_file}")
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON in inputs file: {e}") from e

    if args.inputs:
        try:
            return json.loads(args.inputs)
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON for inputs: {e}") from e

    raise SystemExit("Must provide either --inputs or --inputs-file")

def cmd_add(args: argparse.Namespace) -> None:
    inputs = _load_inputs(args)

    decision = record_decision(
        actor=args.actor,
        title=args.title,
        description=args.description,
        context=args.context,
        inputs=inputs,
        options_considered=args.options,
        tradeoffs=args.tradeoffs,
        tags=args.tags,
        storage_path=args.storage_path,
    )

    print(f"Recorded decision {decision.decision_id}")


def cmd_list(args: argparse.Namespace) -> None:
    start = _validate_iso(args.start)
    end = _validate_iso(args.end)

    decisions = load_decisions(args.storage_path)

    if args.actor:
        decisions = filter_by_actor(decisions, args.actor)

    if args.tag:
        decisions = filter_by_tag(decisions, args.tag)

    if start or end:
        decisions = filter_by_time_range(
            decisions,
            start=start,
            end=end,
        )
    if not decisions:
        if args.json:
            print(json.dumps([], indent=2))
        else:
            print("No decisions found.")
        return

    if args.json:
        print(json.dumps([d.to_dict() for d in decisions], indent=2))
        return

    for d in decisions:
        print(f"{d.timestamp} | {d.actor} | {d.title}")


def _validate_iso(ts: str | None) -> str | None:
    if ts is None:
        return None
    try:
        datetime.fromisoformat(ts)
    except ValueError:
        raise SystemExit(f"Invalid ISO timestamp: {ts}")
    return ts


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

    if not outcomes:
        print(json.dumps([], indent=2) if args.json else "No outcomes found.")
        return

    if args.json:
        print(json.dumps([o.to_dict() for o in outcomes], indent=2))
        return

    for o in outcomes:
        print(f"{o.timestamp} | {o.decision_id} | {o.outcome} | {o.notes or ''}")


def cmd_stats(args: argparse.Namespace) -> None:
    decisions = load_decisions(args.storage_path)
    outcomes = load_outcomes(args.outcome_storage_path)

    if args.json:
        payload = {
            "total_decisions": decision_count(decisions),
            "total_outcomes": outcome_count(outcomes),
            "by_actor": dict(sorted(count_by_actor(decisions).items())),
            "by_tag": dict(sorted(count_by_tag(decisions).items())),
        }
        print(json.dumps(payload, indent=2))
        return

    print(f"Total decisions: {decision_count(decisions)}")
    print(f"Total outcomes: {outcome_count(outcomes)}")

    by_actor = count_by_actor(decisions)
    if by_actor:
        print("\nBy actor:")
        for actor, count in by_actor.items():
            print(f"  {actor}: {count}")

    by_tag = count_by_tag(decisions)
    if by_tag:
        print("\nBy tag:")
        for tag, count in by_tag.items():
            print(f"  {tag}: {count}")


def cmd_export(args: argparse.Namespace) -> None:
    decisions = load_decisions(args.storage_path)

    if args.actor:
        decisions = filter_by_actor(decisions, args.actor)

    if args.tag:
        decisions = filter_by_tag(decisions, args.tag)

    start = _validate_iso(args.start)
    end = _validate_iso(args.end)

    if start or end:
        decisions = filter_by_time_range(
            decisions,
            start=start,
            end=end,
        )


    if args.format == "csv":
        export_decisions_csv(decisions, args.output)
        print(f"Exported {len(decisions)} decisions to {args.output}")



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
    group = add.add_mutually_exclusive_group(required=True)
    group.add_argument("--inputs", help="Raw JSON string of inputs")
    group.add_argument("--inputs-file", help="Path to JSON file containing inputs")

    add.add_argument("--options", nargs="*")
    add.add_argument("--tradeoffs")
    add.add_argument("--tags", nargs="*")

    list_cmd = subparsers.add_parser("list", help="List recorded decisions")
    list_cmd.set_defaults(func=cmd_list)

    list_cmd.add_argument("--actor")
    list_cmd.add_argument("--tag")
    list_cmd.add_argument("--start", help="ISO start timestamp")
    list_cmd.add_argument("--end", help="ISO end timestamp")
    list_cmd.add_argument("--json", action="store_true", help="Output as JSON")

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

    stats_cmd = subparsers.add_parser("stats", help="Show aggregate metrics")
    stats_cmd.set_defaults(func=cmd_stats)
    stats_cmd.add_argument(
        "--outcome-storage-path",
        type=Path,
        default=DEFAULT_OUTCOME_PATH,
    )
    stats_cmd.add_argument("--json", action="store_true")


    export_cmd = subparsers.add_parser("export", help="Export decisions")
    export_cmd.set_defaults(func=cmd_export)
    export_cmd.add_argument("--format", choices=["csv"], required=True)
    export_cmd.add_argument("--output", type=Path, required=True)
    export_cmd.add_argument("--actor")
    export_cmd.add_argument("--tag")
    export_cmd.add_argument("--start")
    export_cmd.add_argument("--end")


    args = parser.parse_args(argv)

    try:
        args.func(args)
    except (RuntimeError, ValueError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)



if __name__ == "__main__":
    main()
