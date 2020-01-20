from typing import Any, List, Tuple

from openapi_core.schema.operations.models import Operation
from openapi_core.schema.specs.models import Spec
from openapi_core.validation.request.validators import (
    RequestValidator as BaseRequestValidator,
)

from .data import OpenAPICoreRequest, OpenAPIParameters, to_openapi_parameters
from .mappings import convert_dict_to_mapping_proxy, enforce_dicts, merge_data


ROOT_PATH = "."


class RequestValidator(BaseRequestValidator):
    """Custom request validator for rororo.

    By default, openapi-core doesn't support proper assigining additional
    properties into the resulted body model, cause of that instead of returning
    Models instances - return casted, but unmarshaled request body data.
    """

    def _get_body(
        self, request: OpenAPICoreRequest, operation: Operation
    ) -> Tuple[Any, List[Exception]]:
        body, errors = super()._get_body(request, operation)
        if errors or not operation.request_body:
            return (body, errors)

        body_with_dicts = enforce_dicts(body)

        media_type = operation.request_body[request.mimetype]
        raw_body = operation.request_body.get_value(request)

        return (
            convert_dict_to_mapping_proxy(
                merge_data(body_with_dicts, media_type.cast(raw_body))
            ),
            errors,
        )


def validate_parameters_and_body(
    spec: Spec, core_request: OpenAPICoreRequest
) -> Tuple[OpenAPIParameters, Any]:
    """
    Instead of validating request parameters & body in two calls, validate them
    at once.
    """
    validator = RequestValidator(spec)
    result = validator.validate(core_request)

    result.raise_for_errors()
    return (
        to_openapi_parameters(result.parameters),
        result.body,
    )
