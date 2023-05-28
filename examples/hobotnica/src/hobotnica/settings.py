"""Settings for Hobotnica example."""

import environ

from rororo import BaseSettings


@environ.config(prefix="", frozen=True)
class Settings(BaseSettings):
    use_error_middleware: bool = environ.bool_var(
        name="USE_ERROR_MIDDLEWARE", default=True
    )
