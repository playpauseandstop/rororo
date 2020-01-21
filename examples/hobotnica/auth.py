from rororo.openapi.exceptions import InvalidCredentials
from .data import GITHUB_PERSONAL_TOKEN, GITHUB_USERNAME


def authenticate(*, username: str, personal_token: str) -> None:
    if username != GITHUB_USERNAME or personal_token != GITHUB_PERSONAL_TOKEN:
        raise InvalidCredentials()
