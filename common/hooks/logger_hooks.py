import logging

from common.scaf_facade import SCAFFacade


def pytest_runtest_logstart(nodeid, location):
    SCAFFacade().logger.logger.name = nodeid
    SCAFFacade().logger.switch_test(location[2])


def pytest_exception_interact(node, call, report):
    if SCAFFacade().logger.log_level == logging.INFO:
        SCAFFacade().logger.log_fail("TEST FAILED")
    else:
        SCAFFacade().logger.log_fail(f"\n{report.longrepr}")
