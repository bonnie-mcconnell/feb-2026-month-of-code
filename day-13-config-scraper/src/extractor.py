from bs4 import BeautifulSoup
import re


_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    text = text.strip()
    return _WHITESPACE_RE.sub(" ", text)


def extract_fields(html: str, field_defs: dict) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    data = {}
    missing = []

    for field_name, definition in field_defs.items():
        selector = definition["selector"]

        try:
            element = soup.select_one(selector)
        except Exception:
            # Invalid selector syntax or parser issue
            element = None

        if element is None:
            data[field_name] = None
            missing.append(field_name)
            continue

        raw_text = element.get_text()
        cleaned = _normalize_text(raw_text)

        data[field_name] = cleaned

    return {
        "data": data,
        "missing_selectors": missing
    }
