from rororo.openapi.exceptions import InvalidCredentials
from .data import GITHUB_PERSONAL_TOKEN, GITHUB_USERNAME


def authenticate(*, username: str, personal_token: str) -> None:
    """
    Authenticate using the given credentials.

    Args:
        username: (str): write your description
        personal_token: (str): write your description
    """
    if username != GITHUB_USERNAME or personal_token != GITHUB_PERSONAL_TOKEN:
        raise InvalidCredentials()
