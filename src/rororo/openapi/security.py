import base64
import binascii
from typing import Union

from aiohttp import BasicAuth, hdrs
from openapi_core.security.exceptions import SecurityError as CoreSecurityError
from openapi_core.security.factories import (
    SecurityProviderFactory as CoreSecurityProviderFactory,
)
from openapi_core.security.providers import (
    ApiKeyProvider as CoreApiKeyProvider,
    HttpProvider as CoreHttpProvider,
)
from openapi_core.validation.request.datatypes import OpenAPIRequest


class ApiKeyProvider(CoreApiKeyProvider):
    def __call__(self, request: OpenAPIRequest) -> str:
        name = self.scheme["name"]
        location = self.scheme["in"]
        source = getattr(request.parameters, location)
        for header_name, header_value in source:
            if name == header_name:
                return header_value
        else:
            raise CoreSecurityError("Missing api key parameter.")


class HttpProvider(CoreHttpProvider):
    def __call__(self, request: OpenAPIRequest) -> Union[BasicAuth, str]:
        for header_name, header_value in request.parameters.header:
            if header_name == hdrs.AUTHORIZATION:
                try:
                    auth_type, encoded_credentials = header_value.split(" ", 1)
                except ValueError:
                    raise CoreSecurityError(
                        "Could not parse authorization header."
                    )
                scheme = self.scheme["scheme"]
                if auth_type.lower() != scheme:
                    raise CoreSecurityError(
                        f"Unknown authorization method {auth_type}"
                    )
                if self.scheme["scheme"] == "basic":
                    try:
                        decoded = base64.b64decode(
                            encoded_credentials.encode("ascii"), validate=True
                        ).decode("latin1")
                    except binascii.Error:
                        raise CoreSecurityError("Invalid base64 encoding.")

                    try:
                        username, password = decoded.split(":", 1)
                    except ValueError:
                        raise CoreSecurityError("Invalid credentials.")
                    return BasicAuth(username, password)
                else:
                    return encoded_credentials
        else:
            raise CoreSecurityError("Missing authorization header.")


class SecurityProviderFactory(CoreSecurityProviderFactory):
    PROVIDERS = {
        **CoreSecurityProviderFactory.PROVIDERS,
        "apiKey": ApiKeyProvider,
        "http": HttpProvider,
    }
