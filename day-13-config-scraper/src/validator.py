def validate_extraction(extraction_result: dict, field_defs: dict) -> dict:
    data = extraction_result["data"]
    missing_selectors = set(extraction_result["missing_selectors"])

    errors = []
    optional_issues = False

    for field_name, definition in field_defs.items():
        required = definition["required"]
        non_empty = definition["non_empty"]

        value = data.get(field_name)

        # Selector missing entirely
        if field_name in missing_selectors:
            if required:
                errors.append(f"missing required field: {field_name}")
            else:
                optional_issues = True
            continue

        # Field present but empty
        if value == "":
            if non_empty:
                if required:
                    errors.append(f"required field empty: {field_name}")
                else:
                    optional_issues = True

    if errors:
        status = "FAILED"
    elif optional_issues:
        status = "PARTIAL"
    else:
        status = "SUCCESS"

    return {
        "status": status,
        "data": data,
        "errors": errors,
    }
