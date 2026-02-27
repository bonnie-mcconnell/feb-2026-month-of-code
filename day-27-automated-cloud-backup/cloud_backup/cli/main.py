import argparse
import os
import sys

from cloud_backup.engine.backup_engine import BackupEngine
from cloud_backup.engine.index_store import IndexStore, IndexCorruptedError
from cloud_backup.storage.local_adapter import LocalStorageAdapter
from cloud_backup.infra.logger import JsonLogger
from cloud_backup.infra.config_loader import load_config, ConfigError
from cloud_backup.storage.s3_adapter import S3StorageAdapter


def main() -> None:
    parser = argparse.ArgumentParser(prog="backup")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-full", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--verify", action="store_true")

    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    logger = JsonLogger(debug=args.debug)

    if config.storage.type == "local":
        assert config.storage.destination is not None
        storage = LocalStorageAdapter(config.storage.destination)
    elif config.storage.type == "s3":
        storage = S3StorageAdapter(
            bucket=config.storage.bucket,
            prefix=config.storage.prefix,
        )
    else:
        print(f"Unsupported storage type: {config.storage.type}", file=sys.stderr)
        sys.exit(1)

    if config.storage.type == "local":
        assert config.storage.destination is not None
        index_path = os.path.join(config.storage.destination, "index.json")
    else:
        index_path = os.path.join(os.getcwd(), ".backup_index.json")

    index_store = IndexStore(index_path)

    engine = BackupEngine(
        config=config,
        storage=storage,
        index_store=index_store,
        logger=logger,
    )

    if args.verify:
        engine.verify()
        return

    try:
        engine.run(
            dry_run=args.dry_run,
            force_full=args.force_full,
        )
    except IndexCorruptedError as e:
        logger.log("index_corrupted", error=str(e))
        sys.exit(1)
    except Exception as e:
        logger.log("backup_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
