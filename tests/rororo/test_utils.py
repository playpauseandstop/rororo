import pytest

from rororo.utils import ensure_collection, to_bool, to_int


@pytest.mark.parametrize(
    "value, expected",
    (
        ("string", ("string",)),
        (("string",), ("string",)),
        ({"string"}, {"string"}),
        (["one", "two"], ["one", "two"]),
    ),
)
def test_ensure_collection(value, expected):
    """
    Assert that value is a test.

    Args:
        value: (todo): write your description
        expected: (todo): write your description
    """
    assert ensure_collection(value) == expected


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
    """
    Convert value to a boolean.

    Args:
        value: (str): write your description
        expected: (str): write your description
    """
    assert to_bool(value) is expected


@pytest.mark.parametrize(
    "value, expected", ((1, 1), ("1", 1), ("does not int", None))
)
def test_to_int(value, expected):
    """
    Convert value is_to_int

    Args:
        value: (str): write your description
        expected: (str): write your description
    """
    assert to_int(value) == expected


@pytest.mark.parametrize("value", (10, [], [1, 2, 3]))
def test_to_int_default_value(value):
    """
    Converts the value to an integer.

    Args:
        value: (str): write your description
    """
    assert to_int("does not int", value) == value
