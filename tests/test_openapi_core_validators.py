import pytest
from jsonschema.exceptions import FormatError

from rororo.openapi.core_validators import EmailFormatter


@pytest.mark.parametrize(
    "invalid_value",
    ("", "not-email", "not-email.com", "https://www.google.com/"),
)
def test_invalid_value(invalid_value):
    with pytest.raises(FormatError) as exc:
        EmailFormatter().validate(invalid_value)
    assert str(exc.value) == f"{invalid_value!r} is not an 'email'"


@pytest.mark.parametrize("value", ("email@domain.com", "EmAiL@domain.com"))
def test_valid_email(value):
    assert EmailFormatter().validate(value) is True
