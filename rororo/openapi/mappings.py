import types
from collections.abc import Mapping
from typing import Any

from openapi_core.extensions.models.models import Model

from ..annotations import T


def convert_dict_to_mapping_proxy(data: Any) -> Any:
    """Convert all dicts to mapping proxy types."""
    if isinstance(data, list):
        return [convert_dict_to_mapping_proxy(item) for item in data]

    if isinstance(data, Mapping):
        return types.MappingProxyType(
            {
                key: convert_dict_to_mapping_proxy(value)
                for key, value in data.items()
            }
        )

    return data


def enforce_dicts(data: Any) -> Any:
    """Deep convert openapi-core Models to dicts."""
    if isinstance(data, list):
        return [enforce_dicts(item) for item in data]

    if isinstance(data, Mapping):
        return {key: enforce_dicts(value) for key, value in data.items()}

    if isinstance(data, Model):
        return {key: enforce_dicts(value) for key, value in vars(data).items()}

    return data


def merge_data(original_data: T, extra_data: Any) -> T:
    if isinstance(original_data, dict) and isinstance(extra_data, Mapping):
        for key, value in extra_data.items():
            if key not in original_data or (
                value and original_data[key] == {}
            ):
                original_data[key] = value
            else:
                original_data[key] = merge_data(original_data[key], value)

    if isinstance(original_data, list) and isinstance(extra_data, list):
        for idx, item in enumerate(extra_data):
            original_data[idx] = merge_data(original_data[idx], item)

    return original_data
