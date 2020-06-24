import pytest
from unit_tests.rest_qa_api_tests.tests_utils import DummyResponseBuilder, TestEndpointBuilder


@pytest.fixture(scope="function")
def response():
    fake_response = DummyResponseBuilder().method().code().header({}).body()
    return fake_response


@pytest.fixture(scope="function")
def builder():
    builder = TestEndpointBuilder()
    builder.endpoint.request_model.allowed_methods = ("get",)
    return builder


def pytest_runtest_logstart(nodeid, location):
    DummyResponseBuilder().set_default_state()
