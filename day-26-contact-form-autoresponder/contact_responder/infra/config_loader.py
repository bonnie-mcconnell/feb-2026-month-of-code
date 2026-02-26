import json
from pathlib import Path

from contact_responder.domain.spam import SpamConfig


def load_spam_config(path: str) -> SpamConfig:
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    return SpamConfig(
        blacklisted_phrases=data["blacklisted_phrases"],
        suspicious_phrases=data["suspicious_phrases"],
        max_links=data["max_links"],
        excessive_length=data["excessive_length"],
        spam_threshold=data["spam_threshold"],
    )