import argparse
import json
import sys

from .config_loader import load_config, ConfigError
from .engine import run_engine
from .errors import FetchError, EngineError

def _print_summary(result: dict) -> None:
    print(f"\nSource: {result['source']}")
    print("-" * 40)

    for entry in result["results"]:
        url = entry["url"]
        status = entry["status"]

        print(f"{url}")
        print(f"  status: {status}")

        if entry["errors"]:
            for err in entry["errors"]:
                print(f"  error: {err}")

        print()

    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(prog="scraper")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="run scraper with config")
    run_parser.add_argument("config", help="path to config json")
    run_parser.add_argument("--output", help="optional path to write json output", default=None)

    args = parser.parse_args()

    if args.command != "run":
        parser.print_help()
        sys.exit(1)

    # Load config
    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        sys.exit(2)


    # Run engine
    try:
        result = run_engine(config)
    except FetchError as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        sys.exit(1)
    except EngineError as e:
        print(f"engine failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"unexpected engine failure: {e}", file=sys.stderr)
        sys.exit(1)

    # Output summary
    _print_summary(result)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            print(f"failed to write output file: {e}", file=sys.stderr)
            sys.exit(1)

    # Determine exit code
    has_failure = any(r["status"] == "FAILED" for r in result["results"])
    if has_failure:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()

