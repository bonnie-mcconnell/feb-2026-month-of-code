import argparse
import sys

from .config import load_config
from .storage import Storage
from .checker import HealthChecker
from .monitor import Monitor


DEFAULT_DB_PATH = "data/uptime.db"
DEFAULT_CONFIG_PATH = "config.json"


def build_monitor() -> Monitor:
    config = load_config(DEFAULT_CONFIG_PATH)

    storage = Storage(DEFAULT_DB_PATH)
    checker = HealthChecker(
        timeout=config.timeout,
        degraded_threshold_ms=config.degraded_threshold_ms,
    )

    return Monitor(storage=storage, checker=checker, urls=config.urls)


def cmd_run(args):
    monitor = build_monitor()
    results = monitor.run_cycle()

    for cycle in results:
        result = cycle.result

        line = f"{result.url} - {result.status}"

        if result.response_time is not None:
            line += f" ({result.response_time} ms)"

        if args.verbose:
            line += f" | error: {result.error or 'none'}"
        print(line)


def cmd_report(args: argparse.Namespace):
    monitor = build_monitor()
    summary = monitor.get_report(args.url)

    if not summary:
        print("No data available.")
        return

    print(f"Report for {args.url}")
    print("-" * 40)
    print(f"Total checks: {summary['total_checks']}")
    print(f"Up count: {summary['up_count']}")
    print(f"Down count: {summary['down_count']}")
    print(f"Degraded count: {summary['degraded_count']}")
    print(f"Downtime count: {summary['down_count']}")
    print(f"Uptime %: {summary['uptime_pct']:.2f}")
    print(f"Last status: {summary['last_status']}")
    print(f"Last check: {summary['last_timestamp']}")


def cmd_history(args):
    monitor = build_monitor()
    history = monitor.get_history(args.url, args.limit)

    if not history:
        print("No history available.")
        return

    for r in history:
        response_time = f"{r.response_time} ms" if r.response_time is not None else "-"
        error = r.error or ""
        print(f"{r.timestamp} | {r.status} | {response_time} | {error}")

def main():
    parser = argparse.ArgumentParser(prog="monitor")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument(
        "--verbose", action="store_true", help="Show full details per check"
    )
    run_parser.set_defaults(func=cmd_run)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("url")
    report_parser.set_defaults(func=cmd_report)

    history_parser = subparsers.add_parser("history")
    history_parser.add_argument("url")
    history_parser.add_argument(
        "--limit", type=int, default=20, help="Number of history entries to show"
    )
    history_parser.set_defaults(func=cmd_history)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
