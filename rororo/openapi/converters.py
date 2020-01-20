import types
from typing import Any

from openapi_core.extensions.models.models import Model


def convert_request_data(data: Any) -> Any:
    """Deep convert openapi-core Models to MappingProxyTypes."""
    if isinstance(data, list):
        return [convert_request_data(item) for item in data]

    if isinstance(data, Model):
        return types.MappingProxyType(
            {
                key: convert_request_data(value)
                for key, value in vars(data).items()
            }
        )

    return data
