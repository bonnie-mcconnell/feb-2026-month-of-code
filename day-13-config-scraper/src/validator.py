def validate_extraction(extraction_result: dict, field_defs: dict) -> dict:
    data = extraction_result["data"]
    missing_selectors = set(extraction_result["missing_selectors"])

    errors = []
    optional_issues = False
    required_failed = False

    for field_name, definition in field_defs.items():
        required = definition["required"]
        non_empty = definition.get("non_empty", False)

        value = data.get(field_name)

        # Selector missing entirely
        if field_name in missing_selectors:
            if required:
                errors.append(f"missing required field: {field_name}")
                required_failed = True
            else:
                optional_issues = True
            continue

        # Field present but empty
        if value == "":
            if non_empty:
                if required:
                    errors.append(f"required field empty: {field_name}")
                    required_failed = True
                else:
                    optional_issues = True

    if required_failed:
        status = "FAILED"
        validated_data = None
    elif optional_issues:
        status = "PARTIAL"
        validated_data = data
    else:
        status = "SUCCESS"
        validated_data = data

    return {
        "status": status,
        "data": validated_data,
        "errors": errors,
    }
