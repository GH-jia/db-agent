from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


@lru_cache
def load_config() -> dict[str, Any]:
    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def get_config_value(key: str, default: Any = None) -> Any:
    config = load_config()
    value: Any = config
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value
