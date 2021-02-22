import re
import time
import logging
from datetime import timedelta
from operator import gt, lt, eq, ne, le, ge
from typing import Union

from common.config_parser.config_dto import WebDriverSettingsDTO, MobileDriverSettingsDTO

logger = logging.getLogger(__name__)


def _smart_assert(actual, expected, comp_operator, msg=None, timeout=None, repeats=None):
    """
    Compare <actual> with <expected> using <operator>.

    :param actual: actual value or function
    :param expected: expected value
    :param comp_operator: One of Comparison Operations function from operator package: [eq, ne, gt, lt, ge, le]
    :param msg: message that will be logged.
    :param timeout: time or value may change
    :param repeats: number of repetitions to check,
        used for calculate sleep time between attempts: where sleep_time = {timeout} / {repeats},
         if not set - sleep time = 1 second
    """
    operator_str = {
        eq: {"positive": "equal with", "negative": "not equal with"},
        ne: {"positive": "not equal with", "negative": "equal with"},
        gt: {"positive": "more than", "negative": "less than"},
        lt: {"positive": "less than", "negative": "more than"},
        ge: {"positive": "more or equal with", "negative": "less or equal with"},
        le: {"positive": "less or equal with", "negative": "more or equal with"}
    }
    op = operator_str[comp_operator]["positive"]
    nop = operator_str[comp_operator]["negative"]

    start_time = time.time()
    end_time = start_time + timeout if timeout else time.time() + 0.5
    sleep_time = (end_time - start_time) / repeats if repeats else 1

    logger.info(msg if msg else "Assert: '{act}' {op} '{exp}'".format(
        act=f"result of '{actual.__name__}' execution" if callable(actual) else actual,
        op=op, exp=expected))

    while time.time() < end_time:
        act = actual() if callable(actual) else actual
        if comp_operator(act, expected):
            logger.info("\tAssertion passed in {s} seconds: {act} {op} {exp}".format(
                s=int(time.time() - start_time), act=act, op=op, exp=expected))
            break
        elif time.time() + sleep_time + 0.5 < end_time:
            logger.info("'{act}' {op} '{exp}', try again in {time} seconds".format(
                act=act, op=nop, exp=expected, time=sleep_time))
            time.sleep(sleep_time)
        else:
            fail_test("Assertion failed: '{act}' {op} '{exp}'".format(act=act, op=nop, exp=expected))


def assert_should_be_equal(actual_value, expected_value, message=None, timeout=None, repeats=None):
    """
    Assert <actual> is equal with <expected>.
    """
    _smart_assert(actual=actual_value, expected=expected_value, comp_operator=eq,
                  msg=message, timeout=timeout, repeats=repeats)


def assert_should_be_not_equal(actual_value, expected_value, message=None, timeout=None, repeats=None):
    """
    Assert <actual> is not equal with <expected>
    """
    _smart_assert(actual=actual_value, expected=expected_value, comp_operator=ne,
                  msg=message, timeout=timeout, repeats=repeats)


def assert_should_be_greater_than(actual_value, expected_value, message=None, timeout=None, repeats=None):
    """
    Assert <actual> is greater than <expected>.
    """
    _smart_assert(actual=actual_value, expected=expected_value, comp_operator=gt,
                  msg=message, timeout=timeout, repeats=repeats)


def assert_should_be_less_than(actual_value, expected_value, message=None, timeout=None, repeats=None):
    """
    Assert <actual> is less than <expected>.
    """
    _smart_assert(actual=actual_value, expected=expected_value, comp_operator=lt,
                  msg=message, timeout=timeout, repeats=repeats)


def assert_should_contain(actual_value, expected_value, message=None, timeout=None):
    """
    Assert <actual_value> contains in <expected_value>.
    :param actual_value: actual value that should be part of <expected_value>
    :param expected_value: expected value that should contain <actual_value>
    :param message: message that will be logged.
    :param timeout: time or value may change
    """
    logger.info(message or f"Assert: '{actual_value}' contains in '{expected_value}'")

    start_time = time.time()
    end_time = start_time + timeout if timeout else time.time() + 0.5
    sleep_time = (end_time - start_time) / 10

    while time.time() < end_time:
        act = actual_value() if callable(actual_value) else actual_value
        exp = expected_value() if callable(expected_value) else expected_value
        if act in exp:
            logger.info(f"Assertion Passed: '{act}' in '{exp}'")
            break
        elif time.time() + sleep_time + 0.5 < end_time:
            logger.info(f"There is no Actual value in expected: '{act}' not in '{exp}',"
                        f" try again in {sleep_time} seconds")
            time.sleep(sleep_time)
        else:
            fail_test(
                "Assertion Failed: There is no Actual value in expected: '{0}' not in '{1}'".format(
                    act, exp))


def assert_should_not_contain(actual_value, expected_value, message=None):
    """
    Assert <actual_value> is not contained in <expected_value>.
    :param actual_value: actual value that should not be a part of <expected_value>
    :param expected_value: expected value that should not contain <actual_value>
    :param message: message that will be logged.
    """
    logger.info(
        message if message else "Assert: '{act}' not contains in '{exp}'".format(
            act=actual_value, exp=expected_value))

    if actual_value not in expected_value:
        logger.info(
            "Assertion Passed: Actual value is not part of expected: '{act}' not in '{exp}'".format(
                act=actual_value, exp=expected_value))
    else:
        fail_test(
            "Assertion Failed: Actual value is part of expected: '{0}' in '{1}'".format(
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


def assert_dict_should_contains(actual_value, expected_value, message=None, timeout=None):
    """
    Assert that dict <actual> contains all elements from sub-dict <expected>.
    :param actual_value: dict object, that should contain <expected> dict or function to get dict
    :param expected_value: dict object that should be a part of <actual> dict
    :param message: message that will be logged.
    :param timeout: timeout to wait correct value
    """
    def _is_subset(subset, superset):
        if isinstance(subset, dict):
            return all(key in superset and _is_subset(val, superset[key]) for key, val in subset.items())
        # assume that subset is a plain value if none of the above match
        return subset == superset

    start_time = time.time()
    end_time = start_time + timeout if timeout else time.time() + 0.5
    sleep_time = (end_time - start_time) / 10

    logger.info(message or f"Assert: '{actual_value}' in '{expected_value}'")
    while time.time() < end_time:
        act = actual_value() if callable(actual_value) else actual_value
        if act and _is_subset(subset=expected_value, superset=act) is True:
            logger.info(f"Assertion Passed: '{expected_value}' in '{act}'")
            break
        elif time.time() + sleep_time + 0.5 < end_time:
            logger.info(f"Assertion failed: {act} not contain {expected_value}, try again in {sleep_time} seconds")
            time.sleep(sleep_time)
        else:
            fail_test(f"Assertion Failed: '{expected_value}' not in '{actual_value}'")


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


def get_wait_seconds(seconds, web_driver_config: Union[WebDriverSettingsDTO, MobileDriverSettingsDTO]):
    if seconds:
        return seconds
    return web_driver_config.default_wait_time
