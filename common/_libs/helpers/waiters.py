from functools import wraps
from operator import eq, lt, ne, gt
from time import sleep
import logging

logger = logging.getLogger(__name__)


def wait_for_return_value(
        function_getter, required_value,
        attempts=10, time_sleep=5, compare_operator='equal'):
    """Run the specified function and expect it to return the
    given return value.

    Args:
        function_getter (func): Callable object without parameters.
        required_value :         Expected value from 'function_getter'.
        attempts (str):         Attempts number.
        time_sleep (str):       Time to wait before the next attempt.
        compare_operator (str): Operator to compare a real
            return value and the required value. Possible values:
            more than | less than | equal | different

    Examples:
        function_getter = functools.partial(os.path.exists, r"D:\temp")
        wait_for_return_value(function_getter, True)
    """
    attempts = int(attempts)
    time_sleep = int(time_sleep)
    operator = {
        "more than": gt,
        "less than": lt,
        "equal": eq,
        "different": ne
    }
    got_value = None
    while attempts > 0:
        got_value = function_getter()
        logger.debug("Condition: {0} {1} {2} ".format(got_value,
                                                      compare_operator,
                                                      required_value))
        if operator[compare_operator](got_value, required_value):
            logger.debug("Condition returned True... Exit")
            return
        attempts -= 1
        logger.debug("Condition returned False")
        logger.debug(
            "{0} attempts left. Wait for {1}".format(attempts,
                                                     time_sleep))
        sleep(time_sleep)

    raise AssertionError(
        "Actual - {}, Expected - {}. From function - {} ".format(
            got_value, required_value, function_getter))


def waiter_wrapper(top_attempts=150,
                   sleep_time=2,
                   exception_types=(AssertionError,),
                   action_on_fail=None):
    """A function that takes a keyword/function with arguments and
    tries to run it until it's finished successfully. It will catch and
    except every exception from 'exception_types'. An exception
    will be raised if the keyword still fails after all attempts.

    Args:
        top_attempts (int):      Attempts number.
        sleep_time (int):        Time to wait before the next attempt.
        exception_types (tuple): Exceptions to catch.
        action_on_fail (func):   Function to run before the next attempt.

    Examples:
        waiter_wrapper(top_attempts, sleep_time)(keyword)(args)
        waiter_wrapper(top_attempts, sleep_time, action_on_fail=some_function)(keyword)(args)

      If 'some_function' needs to have args, it has to be prepared like:
        functools.partial(some_function, fail_args, )

    Where:
      keyword - A keyword/function to run.
      args - Arguments for the keyword.
    """

    def outer_wrapper(keyword):
        @wraps(keyword)
        def inner_wrapper(*args, **kwargs):
            logger.debug('Running keyword {}'.format(keyword))
            for i in range(int(top_attempts)):
                logger.debug('Attempt #{}'.format(i))
                try:
                    result = keyword(*args, **kwargs)
                    break
                except exception_types as err:
                    logger.debug(
                        'Keyword {0} finished unsuccessfully, '
                        'because of following error: {1}'.format(
                            keyword.__name__, err))
                    if i != int(top_attempts) - 1:
                        logger.debug('Waiting %s seconds...' % sleep_time)
                        sleep(int(sleep_time))

                        if action_on_fail is not None:
                            logger.debug(
                                "Trying action on fail {0)..."
                                .format(action_on_fail))
                            action_on_fail()

                    else:
                        logger.debug(
                            'No attempts left while waiting keyword to be '
                            'finished successfully')
                        raise err
            return result

        return inner_wrapper

    return outer_wrapper
