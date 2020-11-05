from random import choice

from rororo.logger import (
    default_logging_dict,
    IgnoreErrorsFilter,
    update_sentry_logging,
)


TEST_SENTRY_DSN = "https://username:password@app.getsentry.com/project-id"


def test_default_logging_dict():
    """
    Default logging defaults.

    Args:
    """
    logging_dict = default_logging_dict("rororo")

    assert logging_dict["filters"]["ignore_errors"]["()"] == IgnoreErrorsFilter
    assert len(logging_dict["formatters"]) == 2
    assert "default" in logging_dict["formatters"]
    assert "naked" in logging_dict["formatters"]

    assert len(logging_dict["handlers"]) == 2
    assert "stdout" in logging_dict["handlers"]
    assert logging_dict["handlers"]["stdout"]["level"] == "DEBUG"
    assert "stderr" in logging_dict["handlers"]
    assert logging_dict["handlers"]["stderr"]["level"] == "WARNING"

    assert len(logging_dict["loggers"]) == 1
    assert "rororo" in logging_dict["loggers"]
    assert logging_dict["loggers"]["rororo"]["handlers"] == [
        "stdout",
        "stderr",
    ]
    assert logging_dict["loggers"]["rororo"]["level"] == "INFO"


def test_default_logging_dict_keyword_arguments():
    """
    Set the default configuration.

    Args:
    """
    logging_dict = default_logging_dict("rororo", level="DEBUG")
    assert logging_dict["loggers"]["rororo"]["level"] == "DEBUG"


def test_default_logging_dict_multiple_loggers():
    """
    Test if there are any default values.

    Args:
    """
    logging_dict = default_logging_dict("rororo", "tests")

    assert len(logging_dict["loggers"]) == 2
    assert "rororo" in logging_dict["loggers"]
    assert "tests" in logging_dict["loggers"]


def test_ignore_errors_filter():
    """
    Convert filter filter filter.

    Args:
    """
    filter_obj = IgnoreErrorsFilter()

    debug = type("FakeRecord", (object,), {"levelname": "DEBUG"})()
    info = type("FakeRecord", (object,), {"levelname": "INFO"})()
    warning = type("FakeRecord", (object,), {"levelname": "WARNING"})()
    error = type("FakeRecord", (object,), {"levelname": "ERROR"})()
    critical = type("FakeRecord", (object,), {"levelname": "CRITICAL"})()

    assert filter_obj.filter(debug) is True
    assert filter_obj.filter(info) is True
    assert filter_obj.filter(warning) is False
    assert filter_obj.filter(error) is False
    assert filter_obj.filter(critical) is False


def test_update_sentry_logging():
    """
    Update the log entries to log file.

    Args:
    """
    logging_dict = default_logging_dict("rororo")
    update_sentry_logging(logging_dict, TEST_SENTRY_DSN, "rororo")
    assert "sentry" in logging_dict["handlers"]
    assert "sentry" in logging_dict["loggers"]["rororo"]["handlers"]


def test_update_sentry_logging_empty_dsn():
    """
    Update logging log entries dict

    Args:
    """
    empty = choice((False, None, ""))

    logging_dict = default_logging_dict("rororo")
    update_sentry_logging(logging_dict, empty, "rororo")

    assert "sentry" not in logging_dict["handlers"]
    assert "sentry" not in logging_dict["loggers"]["rororo"]["handlers"]


def test_update_sentry_logging_empty_loggers():
    """
    Update the sentry dict to loggers.

    Args:
    """
    logging_dict = default_logging_dict("rororo", "tests")
    update_sentry_logging(logging_dict, TEST_SENTRY_DSN)
    assert "sentry" in logging_dict["loggers"]["rororo"]["handlers"]
    assert "sentry" in logging_dict["loggers"]["tests"]["handlers"]


def test_update_sentry_logging_ignore_sentry():
    """
    Update the sentry dict to log entries.

    Args:
    """
    logging_dict = default_logging_dict("rororo", "tests")
    logging_dict["loggers"]["rororo"]["ignore_sentry"] = True
    update_sentry_logging(logging_dict, TEST_SENTRY_DSN)
    assert "sentry" not in logging_dict["loggers"]["rororo"]["handlers"]
    assert "sentry" in logging_dict["loggers"]["tests"]["handlers"]


def test_update_sentry_logging_kwargs():
    """
    Update the default logging config.

    Args:
    """
    logging_dict = default_logging_dict("rororo")
    update_sentry_logging(logging_dict, TEST_SENTRY_DSN, key="value")
    assert logging_dict["handlers"]["sentry"]["key"] == "value"


def test_update_sentry_logging_missed_logger():
    """
    Update the log entries to log entries to logging.

    Args:
    """
    logging_dict = default_logging_dict("rororo")
    update_sentry_logging(
        logging_dict, TEST_SENTRY_DSN, "rororo", "does-not-exist"
    )


def test_update_sentry_logging_overwrite_level():
    """
    Update the default log level.

    Args:
    """
    logging_dict = default_logging_dict("rororo")
    update_sentry_logging(logging_dict, TEST_SENTRY_DSN, level="INFO")
    assert logging_dict["handlers"]["sentry"]["level"] == "INFO"
