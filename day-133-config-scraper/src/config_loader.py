import json
from pathlib import Path


class ConfigError(Exception):
    pass


def load_config(path: str) -> dict:
    config_path = Path(path)

    if not config_path.exists():
        raise ConfigError(f"config file not found: {path}")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"invalid JSON: {e}") from e

    if not isinstance(raw, dict):
        raise ConfigError("config root must be an object")

    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ConfigError("config must include non-empty 'name'")

    targets = raw.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ConfigError("'targets' must be a non-empty list")

    validated_targets = []

    for i, target in enumerate(targets):
        if not isinstance(target, dict):
            raise ConfigError(f"target[{i}] must be an object")

        url = target.get("url")
        if not isinstance(url, str) or not url.strip():
            raise ConfigError(f"target[{i}] missing valid 'url'")

        fields = target.get("fields")
        if not isinstance(fields, dict) or not fields:
            raise ConfigError(f"target[{i}] must define non-empty 'fields'")

        validated_fields = {}

        for field_name, field_def in fields.items():
            if not isinstance(field_name, str) or not field_name.strip():
                raise ConfigError(f"target[{i}] has invalid field name")

            if not isinstance(field_def, dict):
                raise ConfigError(
                    f"field '{field_name}' in target[{i}] must be an object"
                )

            selector = field_def.get("selector")
            if not isinstance(selector, str) or not selector.strip():
                raise ConfigError(
                    f"field '{field_name}' in target[{i}] missing valid 'selector'"
                )

            required = field_def.get("required", False)
            non_empty = field_def.get("non_empty", False)

            if not isinstance(required, bool):
                raise ConfigError(
                    f"'required' must be boolean in field '{field_name}'"
                )

            if not isinstance(non_empty, bool):
                raise ConfigError(
                    f"'non_empty' must be boolean in field '{field_name}'"
                )

            validated_fields[field_name] = {
                "selector": selector.strip(),
                "required": required,
                "non_empty": non_empty,
            }

        validated_targets.append(
            {
                "url": url.strip(),
                "fields": validated_fields,
            }
        )

    return {
        "name": name.strip(),
        "targets": validated_targets,
    }
