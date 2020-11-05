import datetime

import pytest

from rororo.timedelta import (
    str_to_timedelta,
    timedelta_average,
    timedelta_div,
    timedelta_seconds,
    timedelta_to_str,
)


EMPTY = datetime.timedelta()
HOUR = datetime.timedelta(hours=1)
TWO_HOURS = HOUR * 2
FOUR_HOURS = HOUR * 4
SIX_HOURS = HOUR * 6


def test_str_to_timedelta_default():
    """
    Convert a timedelta to a string.

    Args:
    """
    assert str_to_timedelta("10:00") == datetime.timedelta(hours=10)


def test_str_to_timedelta_multiple_formats():
    """
    Convert timedelta to timedelta.

    Args:
    """
    assert str_to_timedelta("10:20", ("F", "f", "G:i")) == datetime.timedelta(
        hours=10, minutes=20
    )


def test_str_to_timedelta_user_format():
    """
    Convert a string to - readable string.

    Args:
    """
    assert str_to_timedelta("10:20:30", "G:i:s") == datetime.timedelta(
        hours=10, minutes=20, seconds=30
    )


def test_str_to_timedelta_wrong_format():
    """
    Convert a timedelta to a timedelta.

    Args:
    """
    with pytest.raises(ValueError):
        str_to_timedelta("10:00", "abc")


@pytest.mark.parametrize("wrong_value", ((datetime.timedelta(), 10)))
def test_str_to_timedelta_wrong_value(wrong_value):
    """
    Converts the given delta string to a timedelta.

    Args:
        wrong_value: (todo): write your description
    """
    with pytest.raises(ValueError):
        str_to_timedelta(wrong_value)


def test_str_to_timedelta_wrong_value_for_default_format():
    """
    Converts a string to a timedelta.

    Args:
    """
    assert str_to_timedelta("wrong value") is None


def test_str_to_timedelta_wrong_value_for_user_format():
    """
    Convert a timedelta to a timedelta.

    Args:
    """
    with pytest.raises(ValueError):
        str_to_timedelta("wrong value", "G:i")


def test_timedelta_average():
    """
    Èi̇·åıĸæīĳľè¡¨ĭ

    Args:
    """
    assert timedelta_average(TWO_HOURS, FOUR_HOURS, SIX_HOURS) == FOUR_HOURS


@pytest.mark.parametrize(
    "value",
    ([TWO_HOURS, FOUR_HOURS, SIX_HOURS], (TWO_HOURS, FOUR_HOURS, SIX_HOURS)),
)
def test_timedelta_average_as_list_or_tuple(value):
    """
    Takes a value or list.

    Args:
        value: (todo): write your description
    """
    assert timedelta_average(value) == FOUR_HOURS


def test_timedelta_div():
    """
    Test if a timedelta.

    Args:
    """
    assert timedelta_div(TWO_HOURS, FOUR_HOURS) == 0.5


@pytest.mark.parametrize(
    "first, second, expected", ((EMPTY, HOUR, 0), (HOUR, EMPTY, None))
)
def test_timedelta_div_empty(first, second, expected):
    """
    Test if two elements are empty.

    Args:
        first: (todo): write your description
        second: (todo): write your description
        expected: (str): write your description
    """
    assert timedelta_div(first, second) == expected


def test_timedelta_seconds():
    """
    Test if the number of a given timedelta object.

    Args:
    """
    assert timedelta_seconds(HOUR) == 3600


def test_timedelta_seconds_empty():
    """
    Returns a datetime. timedelta is not empty.

    Args:
    """
    assert timedelta_seconds(datetime.timedelta()) == 0


def test_timedelta_seconds_multiple_days():
    """
    Returns a timedelta has a timedelta.

    Args:
    """
    value = datetime.timedelta(days=2, hours=4, minutes=5, seconds=20)
    assert timedelta_seconds(value) == 187520


@pytest.mark.parametrize(
    "fmt, expected",
    (
        ("F", "1:20:30"),
        ("f", "1:20:30"),
        ("G:i", "1:20"),
        ("G:i:s", "1:20:30"),
        ("H:i", "01:20"),
        ("H:i:s", "01:20:30"),
        ("R", "1:20:30"),
        ("r", "1:20:30"),
        ("s", "30"),
    ),
)
def test_timedelta_to_str(fmt, expected):
    """
    Convert a string to a datetime. timedelta object.

    Args:
        fmt: (str): write your description
        expected: (list): write your description
    """
    value = datetime.timedelta(hours=1, minutes=20, seconds=30)
    assert timedelta_to_str(value, fmt) == expected


@pytest.mark.parametrize(
    "fmt, expected",
    (
        ("F", "1 day, 12:20:30"),
        ("f", "1d 12:20:30"),
        ("R", "1 day, 12:20:30"),
        ("r", "1d 12:20:30"),
    ),
)
def test_timedelta_to_str_full_days(fmt, expected):
    """
    Test if the given number of seconds.

    Args:
        fmt: (todo): write your description
        expected: (list): write your description
    """
    value = datetime.timedelta(hours=36, minutes=20, seconds=30)
    assert timedelta_to_str(value, fmt) == expected


@pytest.mark.parametrize(
    "fmt, expected",
    (
        ("F", "2 weeks, 0:00"),
        ("f", "2w 0:00"),
        ("R", "14 days, 0:00:00"),
        ("r", "14d 0:00:00"),
    ),
)
def test_timedelta_to_str_full_no_seconds(fmt, expected):
    """
    Convert a timedelta to a timedelta.

    Args:
        fmt: (todo): write your description
        expected: (list): write your description
    """
    value = datetime.timedelta(hours=336)
    assert timedelta_to_str(value, fmt) == expected


@pytest.mark.parametrize(
    "fmt, expected",
    (
        ("F", "1 week, 1:30"),
        ("f", "1w 1:30"),
        ("R", "7 days, 1:30:00"),
        ("r", "7d 1:30:00"),
    ),
)
def test_timedelta_to_str_full_weeks(fmt, expected):
    """
    Convert a timedelta to a timedelta.

    Args:
        fmt: (todo): write your description
        expected: (list): write your description
    """
    value = datetime.timedelta(hours=169, minutes=30)
    assert timedelta_to_str(value, fmt) == expected


def test_timedelta_to_str_default():
    """
    Convert datetime.

    Args:
    """
    assert timedelta_to_str(datetime.timedelta(days=1, hours=2)) == "26:00"


@pytest.mark.parametrize(
    "wrong_value", ("10:20", datetime.date.today(), datetime.datetime.utcnow())
)
def test_timedelta_to_str_wrong_value(wrong_value):
    """
    Convert a timedelta to a timedelta.

    Args:
        wrong_value: (todo): write your description
    """
    with pytest.raises(ValueError):
        timedelta_to_str(wrong_value)
