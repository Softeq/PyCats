import pytest

from common.scaf_facade import SCAFFacade

# TODO - make it independent
facade = SCAFFacade()
facade.setup_config(None)
facade.setup_logger(None)

from common.rest_qa_api.tests.tests_utils import DummyResponseBuilder, TestEndpointBuilder


@pytest.fixture(scope="function")
def response():
    response = DummyResponseBuilder().method().code().header({}).body()
    return response


@pytest.fixture(scope="function")
def builder():
    builder = TestEndpointBuilder()
    builder.endpoint.request_model.allowed_methods = ("get",)
    return builder


def pytest_runtest_logstart(nodeid, location):
    DummyResponseBuilder().set_default_state()
