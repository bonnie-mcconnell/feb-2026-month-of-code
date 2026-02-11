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

    for r in results:
        status_line = f"{r.url} - {r.status}"
        if r.response_time is not None:
            status_line += f" ({r.response_time} ms)"
        print(status_line)


def cmd_report(args):
    monitor = build_monitor()
    summary = monitor.get_report(args.url)

    if not summary:
        print("No data available.")
        return

    print(f"Report for {args.url}")
    print("-" * 40)
    print(f"Total checks: {summary['total_checks']}")
    print(f"Uptime %: {summary['uptime_pct']:.2f}")
    print(f"Downtime count: {summary['down_count']}")
    print(f"Last status: {summary['last_status']}")
    print(f"Last check: {summary['last_timestamp']}")


def cmd_history(args):
    monitor = build_monitor()
    history = monitor.get_history(args.url, limit=20)

    if not history:
        print("No history available.")
        return

    for r in history:
        print(
            f"{r.timestamp} | {r.status} | "
            f"{r.response_time} ms | {r.error or ''}"
        )


def main():
    parser = argparse.ArgumentParser(prog="monitor")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(func=cmd_run)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("url")
    report_parser.set_defaults(func=cmd_report)

    history_parser = subparsers.add_parser("history")
    history_parser.add_argument("url")
    history_parser.set_defaults(func=cmd_history)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
