from typing import Dict, Any, List, Optional

# Output contract types
OUTPUT_SCHEMA = {
    "source": str,
    "results": [
        {
            "url": str,
            "status": str,       # "SUCCESS" | "PARTIAL" | "FAILED"
            "data": Optional[dict],  # Can be None if extraction failed
            "errors": List[str],      # Always a list
        }
    ],
}


def get_schema_errors(output: Dict[str, Any]) -> List[str]:
    """
    Returns a list of errors if the output does not conform to schema.
    Returns empty list if valid.
    """
    errors: List[str] = []

    # Top-level keys
    if "source" not in output:
        errors.append("Missing top-level 'source' key")
    if "results" not in output:
        errors.append("Missing top-level 'results' key")
    elif not isinstance(output["results"], list):
        errors.append("'results' must be a list")

    # Per-target validation
    if "results" in output and isinstance(output["results"], list):
        for idx, result in enumerate(output["results"]):
            if not isinstance(result, dict):
                errors.append(f"Result at index {idx} is not a dict")
                continue
            for key in ["url", "status", "data", "errors"]:
                if key not in result:
                    errors.append(f"Missing key '{key}' in result at index {idx}")

            # Type checks
            if "url" in result and not isinstance(result["url"], str):
                errors.append(f"'url' must be str at index {idx}")
            if "status" in result and not isinstance(result["status"], str):
                errors.append(f"'status' must be str at index {idx}")
            if "data" in result and not (isinstance(result["data"], dict) or result["data"] is None):
                errors.append(f"'data' must be dict or None at index {idx}")
            if "errors" in result:
                if not isinstance(result["errors"], list):
                    errors.append(f"'errors' must be list at index {idx}")
                else:
                    for e in result["errors"]:
                        if not isinstance(e, str):
                            errors.append(f"All 'errors' elements must be str at index {idx}")

    return errors


def validate_output_schema(output: Dict[str, Any]) -> bool:
    """
    Returns True if output conforms to schema, False otherwise.
    """
    return len(get_schema_errors(output)) == 0
