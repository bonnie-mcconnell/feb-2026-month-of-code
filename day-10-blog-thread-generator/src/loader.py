from pathlib import Path
from typing import Tuple


SUPPORTED_EXTENSIONS = {
    ".txt": "plain",
    ".md": "markdown",
    ".markdown": "markdown",
}


def load_input(path_str: str) -> Tuple[str, str]:
    path = Path(path_str)

    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS.keys())}"
        )

    try:
        raw_text = path.read_text(encoding="utf-8")
    except Exception as exc:
        raise IOError(f"Failed to read input file: {exc}")

    # Normalize line endings early to avoid downstream edge cases
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    detected_format = SUPPORTED_EXTENSIONS[ext]
    return normalized, detected_format
 