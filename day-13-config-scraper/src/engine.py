from .fetcher import fetch_url
from .extractor import extract_fields
from .validator import validate_extraction


def run_engine(config: dict) -> dict:
    source_name = config["name"]
    targets = config["targets"]

    results = []

    for target in targets:
        url = target["url"]
        field_defs = target["fields"]

        # --- Fetch ---
        fetch_result = fetch_url(url)

        if not fetch_result["ok"]:
            errors = [fetch_result["error"]]
            if fetch_result["status_code"] is not None:
                errors.append(f"status_code: {fetch_result['status_code']}")

            results.append({
                "url": url,
                "status": "FAILED",
                "data": None,
                "errors": errors,
            })
            continue

        html = fetch_result["content"]

        # --- Extract + Validate ---
        try:
            extraction = extract_fields(html, field_defs)
            validation = validate_extraction(extraction, field_defs)

            results.append({
                "url": url,
                "status": validation["status"],
                "data": validation["data"],
                "errors": validation["errors"],
            })

        except Exception as e:
            # Unexpected parsing/logic failure
            results.append({
                "url": url,
                "status": "FAILED",
                "data": None,
                "errors": [f"engine_error: {str(e)}"],
            })

    return {
        "source": source_name,
        "results": results,
    }
