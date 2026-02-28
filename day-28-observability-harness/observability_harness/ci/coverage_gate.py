from pathlib import Path
import xml.etree.ElementTree as ET


def enforce_coverage(minimum: float, coverage_file: Path) -> None:
    if not coverage_file.exists():
        raise SystemExit("Coverage XML file not found.")

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
    except ET.ParseError as exc:
        raise SystemExit(f"Malformed coverage XML: {exc}") from exc

    coverage_attr = root.attrib.get("line-rate")
    if coverage_attr is None:
        raise SystemExit("Coverage XML missing 'line-rate' attribute.")

    coverage = float(coverage_attr) * 100

    if coverage < minimum:
        raise SystemExit(
            f"Coverage {coverage:.2f}% below required minimum {minimum}%."
        )