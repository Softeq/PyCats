import logging

from common.pycats_facade import PyCatsFacade


def pytest_runtest_logstart(nodeid, location):
    PyCatsFacade().logger.logger.name = nodeid
    PyCatsFacade().logger.switch_test(location[2])


def pytest_exception_interact(node, call, report):
    if PyCatsFacade().logger.log_level == logging.INFO:
        PyCatsFacade().logger.log_fail("TEST FAILED")
    else:
        PyCatsFacade().logger.log_fail(f"\n{report.longrepr}")
