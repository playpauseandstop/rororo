import pytest

from rororo.utils import to_bool, to_int


@pytest.mark.parametrize(
    "value, expected",
    (
        ("1", True),
        ("0", False),
        ("y", True),
        ("n", False),
        (1, True),
        (0, False),
        ([1, 2, 3], True),
        ([], False),
    ),
)
def test_to_bool(value, expected):
    assert to_bool(value) is expected


@pytest.mark.parametrize(
    "value, expected", ((1, 1), ("1", 1), ("does not int", None))
)
def test_to_int(value, expected):
    assert to_int(value) == expected


@pytest.mark.parametrize("value", (10, [], [1, 2, 3]))
def test_to_int_default_value(value):
    assert to_int("does not int", value) == value
