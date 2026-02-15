import json
from pathlib import Path

SECTOR_PATH = Path("config/sector_weights.json")


def load_sector_weights():
    if not SECTOR_PATH.exists():
        return {}

    with open(SECTOR_PATH) as f:
        return json.load(f)
