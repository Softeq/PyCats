from unittest.mock import patch

import json
import pytest
from common._rest_qa_api.rest_exceptions import RestResponseValidationError
from common._rest_qa_api.rest_checkers import JSONCheckers, check_status
from unit_tests.rest_qa_api_tests.tests_utils import DummyResponseBuilder


def fake_response():
    return DummyResponseBuilder().method().code().header({}).body()


@pytest.fixture(scope="function", autouse=True)
def reset_checker_status():
    JSONCheckers.status = None
    JSONCheckers.expected_json_structure = None


@patch('requests.request', return_value=fake_response())
class TestRunCheckersBranches:

    def test_calling_of_multiple_custom_checkers(self, _, response, builder):
        JSONCheckers.status = 200
        JSONCheckers.expected_json_structure = {"testKey1": ["testValue1", "testValue2"]}
        response.body(json.dumps({"testKey2": ["testValue1", "testValue2"]}))
        response.status_code = 500
        builder.endpoint.response_model.custom_checkers.append(JSONCheckers)
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"Invalid status code. Expected '{JSONCheckers.status}', but got '{response.status_code}'" \
               and f"Invalid JSON Structure" in str(excinfo.value)

    def test_custom_checkers_isinstance_branch(self, _, response, builder):
        JSONCheckers.status = 200
        JSONCheckers.deactivate(JSONCheckers.check_json_structure)
        builder.endpoint.response_model.custom_checkers.append(JSONCheckers)
        response.status_code = 400
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"Checker 'check_status' failed with error: Invalid status code. Expected '{JSONCheckers.status}', " \
               f"but got '{response.status_code}'" in str(excinfo.value)

    def test_function_call_and_assertion_branch_for_customer_checkers(self, _, response, builder):
        response.status_code = 400
        check_status_code = 200
        builder.endpoint.response_model.custom_checkers.append(check_status(check_status_code))
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"Invalid status code. Expected '{check_status_code}', " \
               f"but got '{response.status_code}'" in str(excinfo.value)

    def test_unsupported_type_for_customer_checkers(self, _, response, builder):
        builder.endpoint.response_model.custom_checkers.append(DummyResponseBuilder)
        with pytest.raises(TypeError) as excinfo:
            builder.endpoint.get()
        assert f"{DummyResponseBuilder} has unsupported type. Supported are " \
               f"functions and BaseRESTCheckers instances" in str(excinfo.value)

    def test_exceptions_for_customer_checkers(self, _, response, builder, caplog):
        builder.endpoint.response_model.custom_checkers.append(DummyResponseBuilder)
        with pytest.raises(Exception):
            builder.endpoint.get()
        expected_log_message = "fail"
        expected_second_log_message = f"<class 'unit_tests.rest_qa_api_tests.tests_utils.DummyResponseBuilder'> has" \
                                      f" unsupported type. Supported are functions and BaseRESTCheckers instances"
        first_message = [record for record in caplog.records if expected_log_message == record.message]
        second_message = [record for record in caplog.records if expected_second_log_message == record.message]
        assert len(first_message) == 1 and len(second_message) == 1, "Expected messages not found in logs"


@patch('requests.request', return_value=fake_response())
class TestCustomLogger:

    def test_logging_after_successful_execution_of_custom_checker(self, _, response, builder, caplog):
        JSONCheckers.status = 200
        JSONCheckers.deactivate(JSONCheckers.check_json_structure)
        builder.endpoint.response_model.custom_checkers.append(JSONCheckers)
        response.status_code = 200
        try:
            builder.endpoint.get()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")
        expected_first_log_message = f"run checker: {JSONCheckers.__name__}: "
        expected_second_log_message = f"check that status code is {JSONCheckers.status}"
        expected_third_log_message = f"{JSONCheckers.check_status.__name__} validation passed"
        expected_fourth_log_message = f"{JSONCheckers.__name__} validation passed"
        messages = [record for record in caplog.records if record.message in
                    (expected_first_log_message, expected_second_log_message,
                     expected_third_log_message, expected_fourth_log_message)]
        assert len(messages) == 4, "Expected message not found in logs"

    def test_logging_through_customer_checker_function(self, _, response, builder, caplog):
        response.status_code = 200
        check_status_code = 200
        builder.endpoint.response_model.custom_checkers.append(check_status(check_status_code))
        try:
            builder.endpoint.get()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")
        expected_log_message = f"{JSONCheckers.check_status.__name__} validation passed"
        messages = [record for record in caplog.records if expected_log_message == record.message]
        assert len(messages) == 1, "Expected message not found in logs"

    def test_logging_format(self, _, response, builder):
        JSONCheckers.status = 200
        JSONCheckers.deactivate(JSONCheckers.check_json_structure)
        builder.endpoint.response_model.custom_checkers.append(JSONCheckers)
        response.status_code = 400
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"\n{'#' * 40}\nCUSTOM RESPONSE VALIDATION FAILED.\n{'#' * 40}\n" in str(excinfo.value)
        
    def test_negative_condition_for_run_checker_function(self, _, response, builder, caplog):
        JSONCheckers.status = 200
        response.status_code = 400
        JSONCheckers.deactivate(JSONCheckers.check_json_structure)
        builder.endpoint.response_model.custom_checkers.append(JSONCheckers)
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"{JSONCheckers.check_status.__name__} validation passed" not in str(excinfo.value)
