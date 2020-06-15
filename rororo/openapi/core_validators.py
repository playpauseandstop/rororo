from collections import deque
from functools import partial
from typing import Any, cast, Dict, Iterator, List, Optional, Tuple

import pyrsistent
from email_validator import EmailNotValidError, validate_email
from isodate import parse_datetime
from jsonschema.exceptions import FormatError
from more_itertools import peekable
from openapi_core.casting.schemas.exceptions import CastError as CoreCastError
from openapi_core.exceptions import OpenAPIError as CoreOpenAPIError
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.paths.models import Path
from openapi_core.schema.schemas.enums import SchemaFormat, SchemaType
from openapi_core.schema.schemas.types import NoValue
from openapi_core.schema.servers.models import Server
from openapi_core.schema.specs.models import Spec
from openapi_core.templating.datatypes import TemplateResult
from openapi_core.templating.paths.exceptions import (
    OperationNotFound,
    PathNotFound,
    ServerNotFound,
)
from openapi_core.templating.paths.finders import PathFinder as CorePathFinder
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory as CoreSchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.unmarshallers import (
    ArrayUnmarshaller as CoreArrayUnmarshaller,
    ObjectUnmarshaller as CoreObjectUnmarshaller,
)
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
)
from openapi_core.validation.request.validators import (
    RequestValidator as CoreRequestValidator,
)
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import (
    ResponseValidator as CoreResponseValidator,
)
from openapi_core.validation.validators import (
    BaseValidator as CoreBaseValidator,
)
from openapi_schema_validator._format import oas30_format_checker

from .data import OpenAPIParameters, to_openapi_parameters
from .exceptions import CastError, ValidationError
from .security import validate_security
from .utils import get_base_url
from ..annotations import MappingStrAny


DATE_TIME_FORMATTER = Formatter.from_callables(
    partial(oas30_format_checker.check, format="date-time"), parse_datetime,
)
PathTuple = Tuple[Path, Operation, Server, TemplateResult, TemplateResult]


class ArrayUnmarshaller(CoreArrayUnmarshaller):
    """Custom array unmarshaller to support nullable arrays.

    To be removed after ``openapi-core`` fixed an issue of supporting nullable
    arrays: https://github.com/p1c2u/openapi-core/issues/251
    """

    def __call__(self, value: Any = NoValue) -> Optional[List[Any]]:
        if value is None and self.schema.nullable:
            return None
        return cast(List[Any], super().__call__(value))


class EmailFormatter(Formatter):
    """Formatter to support email strings.

    Use `email-validator <https://pypi.org/project/email-validator>`_ library
    to ensure that given string is a valid email.
    """

    def validate(self, value: str) -> bool:
        try:
            validate_email(value)
        except EmailNotValidError as err:
            raise FormatError(f"{value!r} is not an 'email'", cause=err)
        return True


class ObjectUnmarshaller(CoreObjectUnmarshaller):
    """Custom object unmarshaller to support nullable objects.

    To be removed after ``openapi-core`` fixed an issue of` supporting nullable
    objects: https://github.com/p1c2u/openapi-core/issues/232
    """

    def __call__(self, value: Any = NoValue) -> Optional[Dict[Any, Any]]:
        if value is None and self.schema.nullable:
            return None
        return cast(Dict[Any, Any], super().__call__(value))


class PathFinder(CorePathFinder):
    """Custom path finder to fix issue with finding paths with vars.

    Temporary fix for https://github.com/p1c2u/openapi-core/issues/226, to be
    removed from *rororo* after next ``openapi-core`` version released with
    proper fix for the issue.
    """

    def find(self, request: OpenAPIRequest) -> PathTuple:
        """Better finder for request path.

        Instead of returning first possible result from
        ``self._get_servers_iter(...)`` call, attempt to ensure that
        ``request.full_url_pattern`` ends with ``path.name``.
        """
        paths_iter_peek = peekable(
            self._get_paths_iter(request.full_url_pattern)
        )
        if not paths_iter_peek:
            raise PathNotFound(request.full_url_pattern)

        operations_iter_peek = peekable(
            self._get_operations_iter(request.method, paths_iter_peek)
        )
        if not operations_iter_peek:
            raise OperationNotFound(request.full_url_pattern, request.method)

        servers_iter: Iterator[PathTuple] = self._get_servers_iter(
            request.full_url_pattern, operations_iter_peek
        )
        for server in servers_iter:
            path = server[0]
            if request.full_url_pattern.endswith(path.name):
                return server

        raise ServerNotFound(request.full_url_pattern)


class SchemaUnmarshallersFactory(CoreSchemaUnmarshallersFactory):
    """
    Custom schema unmarshallers factory to deal with tz aware date time
    strings.

    Temporary fix to https://github.com/p1c2u/openapi-core/issues/235, to be
    removed from *rororo* after next ``openapi-core`` release.
    """

    COMPLEX_UNMARSHALLERS = {
        **CoreSchemaUnmarshallersFactory.COMPLEX_UNMARSHALLERS,
        SchemaType.ARRAY: ArrayUnmarshaller,
        SchemaType.OBJECT: ObjectUnmarshaller,
    }

    def get_formatter(
        self,
        default_formatters: Dict[str, Formatter],
        type_format: str = None,
    ) -> Formatter:
        if type_format == SchemaFormat.DATETIME.value:
            return DATE_TIME_FORMATTER
        return super().get_formatter(default_formatters, type_format)


CUSTOM_FORMATTERS = {"email": EmailFormatter()}


class BaseValidator(CoreBaseValidator):
    """Custom base validator to deal with tz aware date time strings.

    To be removed from *rororo* after next ``openapi-core`` version release.
    """

    def _cast(self, param_or_media_type: Any, value: Any) -> Any:
        try:
            return super()._cast(param_or_media_type, value)
        except CoreCastError as err:
            # Pass param or media type name to cast error
            raise CastError(
                name=param_or_media_type.name, value=err.value, type=err.type
            )

    def _find_path(self, request: OpenAPIRequest) -> PathTuple:
        return PathFinder(self.spec, base_url=self.base_url).find(request)

    def _unmarshal(
        self, param_or_media_type: Any, value: Any, context: UnmarshalContext
    ) -> Any:
        """Use custom unmarshallers factory for unmarsahlling data."""
        if not param_or_media_type.schema:
            return value

        unmarshallers_factory = SchemaUnmarshallersFactory(
            self.spec._resolver, self.custom_formatters, context=context,
        )
        unmarshaller = unmarshallers_factory.create(param_or_media_type.schema)

        try:
            return unmarshaller(value)
        except InvalidSchemaValue as err:
            # Modify invalid schema validation errors to include parameter name
            if isinstance(param_or_media_type, Parameter):
                param_name = param_or_media_type.name

                for schema_error in err.schema_errors:
                    schema_error.path = schema_error.relative_path = deque(
                        [param_name]
                    )

            raise err


class RequestValidator(BaseValidator, CoreRequestValidator):
    def _get_parameters(
        self, request: OpenAPIRequest, params: MappingStrAny
    ) -> Tuple[RequestParameters, List[CoreOpenAPIError]]:
        """
        Distinct parameters errors from body errors to supply proper validation
        error response.
        """
        parameters, errors = super()._get_parameters(request, params)
        if errors:
            raise ValidationError.from_request_errors(
                errors, base_loc=["parameters"]
            )
        return parameters, errors

    def _get_security(
        self, request: OpenAPIRequest, operation: Operation
    ) -> MappingStrAny:
        """
        Custom logic for validating request security, which support handling
        JWT tokens without decoding them from ``base64`` (as needed for
        basic authorization).

        Consider to remove from *rororo* after next ``openapi-core`` release.
        """
        return validate_security(self, request, operation)

    def _unmarshal(  # type: ignore
        self, param_or_media_type: Any, value: Any
    ) -> Any:
        return super()._unmarshal(
            param_or_media_type, value, UnmarshalContext.REQUEST
        )


class ResponseValidator(BaseValidator, CoreResponseValidator):
    def _unmarshal(  # type: ignore
        self, param_or_media_type: Any, value: Any
    ) -> Any:
        return super()._unmarshal(
            param_or_media_type, value, UnmarshalContext.RESPONSE
        )


def validate_core_request(
    spec: Spec, core_request: OpenAPIRequest
) -> Tuple[MappingStrAny, OpenAPIParameters, Any]:
    """
    Instead of validating request parameters & body in two calls, validate them
    at once with passing custom formatters.
    """
    validator = RequestValidator(
        spec,
        custom_formatters=CUSTOM_FORMATTERS,
        base_url=get_base_url(core_request),
    )
    result = validator.validate(core_request)

    if result.errors:
        raise ValidationError.from_request_errors(result.errors)

    return (
        result.security,
        to_openapi_parameters(result.parameters),
        pyrsistent.freeze(result.body),
    )


def validate_core_response(
    spec: Spec, core_request: OpenAPIRequest, core_response: OpenAPIResponse,
) -> Any:
    """Pass custom formatters for validating response data."""
    validator = ResponseValidator(
        spec,
        custom_formatters=CUSTOM_FORMATTERS,
        base_url=get_base_url(core_request),
    )
    result = validator.validate(core_request, core_response)

    if result.errors:
        raise ValidationError.from_response_errors(result.errors)

    return result.data
