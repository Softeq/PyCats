import re
import time
import logging
from datetime import timedelta

import pytz as pytz

from common.libs.config_parser.config_dto import WebDriverSettingsDTO

logger = logging.getLogger(__name__)


def assert_should_be_equal(actual_value, expected_value, message=None,
                           silent=False, timeout=None):
    """
    Assert <actual_value> is equal to <expected_value>.
    :param actual_value: actual value
    :param expected_value: expected value
    :param message: message that will be logged.
    :param silent: logging mod, if true - there is no logging
    :param timeout: time gor value may change
    """
    actual = actual_value() if callable(actual_value) else actual_value
    msg = message if message else "Assert values '{}' and '{}', that should be equal".format(
        actual_value, expected_value)
    logger.info(msg)

    end_time = time.time() + timeout if timeout else time.time() + 1
    sleep_time = (time.time() - end_time) / 5 if (time.time() - end_time) / 5 >= 1 else 1
    while time.time() < end_time:
        actual = actual_value() if callable(actual_value) else actual_value
        if actual == expected_value:
            if not silent:
                logger.info(
                    "Actual value is equal to expected: '{0}' == '{1}'".format(
                        actual, expected_value))
            return None
        else:
            if not silent:
                logger.info(
                    "Actual value isn't equal to expected: '{0}' != '{1}', try again".format(
                        actual, expected_value))
        time.sleep(sleep_time)
    fail_test(
        "Actual value isn't equal to expected: '{0}' != '{1}'".format(actual, expected_value))


def assert_should_be_not_equal(actual_value, expected_value,
                               message=None, silent=False,
                               timeout=None):
    """
    Assert <actual_value> is not equal to <expected_value>.
    :param actual_value: actual value
    :param expected_value: expected value
    :param message: message that will be logged.
    :param silent: logging mod, if true - there is no logging
    :param timeout: time gor value may change
    """
    msg = message if message else "Assert values {} and {}, that should be not equal".format(
        actual_value, expected_value)
    logger.info(msg)

    end_time = time.time() + timeout if timeout else time.time() + 1
    sleep_time = (time.time() - end_time) / 5 if (time.time() - end_time) / 5 >= 1 else 1
    while time.time() < end_time:
        if actual_value != expected_value:
            if not silent:
                logger.info(
                    "Actual value isn't equal to expected: {0} != {1}".format(
                        actual_value, expected_value))
            return None
        else:
            if not silent:
                logger.info(
                    "Actual value is equal to expected: '{0}' == '{1}', try again".format(
                        actual_value, expected_value))
        time.sleep(sleep_time)
    fail_test(
        "Actual value is equal to expected: '{0}' == '{1}'".format(
            actual_value, expected_value))


def assert_should_be_greater_than(actual_value, expected_value,
                                  message=None, silent=False):
    """
    Assert <actual_value> is greater than <expected_value>.
    :param actual_value: actual value
    :param expected_value: expected value
    :param message: message that will be logged.
    :param silent: logging mod, if true - there is no logging
    """
    msg = message if message else "Assert value {} should be greater than {}".format(
        actual_value, expected_value)
    logger.info(msg)

    if actual_value > expected_value:
        if not silent:
            logger.info(
                "Actual value is greater than expected value: {0} > {1}".format(
                    actual_value, expected_value))
    else:
        fail_test(
            "Actual value isn't greater than expected value: '{0}' <= '{1}'"
            .format(actual_value, expected_value))


def assert_should_be_less_than(actual_value, expected_value,
                               message=None, silent=False):
    """
    Assert <actual_value> is less than <expected_value>.
    :param actual_value: actual value
    :param expected_value: expected value
    :param message: message that will be logged.
    :param silent: logging mod, if true - there is no logging
    """
    msg = message if message else "Assert value {} should be less than {}".format(
        actual_value, expected_value)
    logger.info(msg)

    if actual_value < expected_value:
        if not silent:
            logger.info(
                "Actual value is less than expected value: {0} < {1}".format(
                    actual_value, expected_value))
    else:
        fail_test(
            "Actual value isn't less than expected value: '{0}' >= '{1}'"
            .format(actual_value, expected_value))


def assert_should_contain(actual_value, expected_value, message=None,
                          silent=False):
    """
    Assert <actual_value> contains in <expected_value>.
    :param actual_value: actual value that should be part of <expected_value>
    :param expected_value: expected value that should contain <actual_value>
    :param message: message that will be logged.
    :param silent: logging mod, if true - there is no logging
    """
    if actual_value in expected_value:
        if not silent:
            logger.info(
                "Actual value is part of expected: '{act}' in '{exp}'".format(
                    act=actual_value, exp=expected_value))
    else:
        fail_test(
            "There is no Actual value in expected: '{0}' not in '{1}'".format(
                actual_value, expected_value))


def assert_should_not_contain(actual_value, expected_value,
                              message=None, silent=False):
    """
    Assert <actual_value> is not contained in <expected_value>.
    :param actual_value: actual value that should not be a part of <expected_value>
    :param expected_value: expected value that should not contain <actual_value>
    :param message: message that will be logged.
    :param silent: logging mod, if true - there is no logging
    """
    logger.info(
        message if message else "Assert value '{act}' not contains in '{exp}'".format(
            act=actual_value, exp=expected_value))

    if actual_value not in expected_value:
        if not silent:
            logger.info(
                "Actual value is not part of expected: '{act}' not in '{exp}'".format(
                    act=actual_value, exp=expected_value))
    else:
        fail_test(
            "Actual value is contains in expected: '{0}' in '{1}'".format(
                actual_value, expected_value))


def assert_should_match_pattern(actual_value, pattern, message=None):
    """
    Assert <actual_value> is matches pattern <pattern>.
    :param actual_value: actual value that should not be verified
    :param pattern: pattern of string format.
    :param message: message that will be logged.
    """
    logger.info(
        message if message else "Assert is value '{act}' matches pattern '{pattern}'".format(
            act=actual_value,
            pattern=pattern))

    if not re.match(pattern, actual_value):
        fail_test(
            "Actual value '{act}' is not matches pattern '{pattern}'".format(
                act=actual_value, pattern=pattern))


def assert_dates_with_delta(actual_value, expected_value,
                            delta_seconds=0):
    """
    Assert Date delta between <actual_value> and <expected_value> less than <delta_seconds> seconds.
    :param actual_value: actual value, datetime object
    :param expected_value: expected value, datetime object
    :param delta_seconds: possible delta between actual and expected in seconds
    """
    logger.info(
        "Assert that actual '{act}' and expected '{exp}' date differ less than {delta} seconds".format(
            act=actual_value.strftime('%Y-%m-%d %H:%M:%S'),
            exp=expected_value.strftime('%Y-%m-%d %H:%M:%S'),
            delta=delta_seconds))

    difference = actual_value - expected_value
    if difference > timedelta(seconds=delta_seconds):
        fail_test(
            "Difference between '{act}' and '{exp}' more than {delta} seconds".format(
                act=actual_value.strftime('%Y-%m-%d %H:%M:%S'),
                exp=expected_value.strftime('%Y-%m-%d %H:%M:%S'),
                delta=delta_seconds))


def fail_test(message):
    """
    fail test with log
    :param message: message that will be logged.
    """
    logger.log_fail(message)
    assert 0, message


def wait_in_seconds(seconds):
    """
    Sleep {seconds} seconds
    :param seconds:
    :return:
    """
    logger.info(f"Wait {seconds} seconds")
    time.sleep(seconds)


def get_wait_seconds(seconds, webdriver_settings_config: WebDriverSettingsDTO):
    if seconds:
        return seconds
    return webdriver_settings_config.webdriver_default_wait_time


def convert_local_date_to_tz(date_object,
                             timezone="America/Los_Angeles"):
    """
    Convert naive date to <timezone> aware date (LA by default) and return naive datetime object.
    """
    result = date_object.astimezone(pytz.timezone(timezone))
    return result.replace(tzinfo=None)
