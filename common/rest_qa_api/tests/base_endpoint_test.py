from unittest.mock import patch

import pytest
import requests

from common.rest_qa_api.tests.conftest import response
from common.rest_qa_api.base_endpoint import BaseEndpoint
from common.rest_qa_api.rest_utils import SKIP
from common.rest_qa_api.tests.tests_utils import TestEndpointBuilder
from common.rest_qa_api.rest_exceptions import MethodNotSupportedByEndpoint, RestResponseValidationError


@pytest.mark.parametrize("method", ["get"])
def test_not_allowed_public_method_call(method):
    with pytest.raises(MethodNotSupportedByEndpoint) as excinfo:
        test_request_obj = TestEndpointBuilder._TestRequestModel()
        test_request_obj.allowed_methods = ()
        test_response_obj = TestEndpointBuilder._TestResponseModel()
        test_endpoint = BaseEndpoint("", test_request_obj, test_response_obj, None)
        getattr(test_endpoint, method)
    assert f"This Endpoint does not support '{method}' method" in str(excinfo.value)


@pytest.mark.parametrize("method", ["__test"])
def test_allowed_dunder_method_call(method):
    try:
        test_request_obj = TestEndpointBuilder._TestRequestModel()
        test_request_obj.allowed_methods = ()
        test_response_obj = TestEndpointBuilder._TestResponseModel()
        test_endpoint = BaseEndpoint("", test_request_obj, test_response_obj, None)
        getattr(test_endpoint, method)
    except Exception as e:
        pytest.fail(f"DID RAISE {e}")


def test_access_public_fields():
    try:
        test_endpoint = BaseEndpoint("Test", "Test", "Test", "Test")
        assert test_endpoint.base_url
        assert test_endpoint.make_url_method
        assert test_endpoint.request_model
        assert test_endpoint.response_model
    except Exception as e:
        pytest.fail(f"DID RAISE {e}")


@pytest.mark.usefixtures("builder", "builder")
@patch('requests.request', return_value=response())
class TestStatusCode:

    def test_not_equal_status_code(self, _, response, builder):
        builder.endpoint.response_model.status_code = 400
        response.status_code = 200
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"Field 'status_code', expected value '{builder.endpoint.response_model.status_code}', " \
               f"but got '{response.status_code}'" in str(excinfo.value)

    def test_equal_status_code(self, _, response, builder):
        builder.endpoint.response_model.status_code = 200
        response.status_code = 200
        try:
            builder.endpoint.get()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_skip_status_code(self, _, response, builder):
        builder.endpoint.response_model.status_code = SKIP
        response.status_code = 500
        try:
            builder.endpoint.get()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")


@pytest.mark.usefixtures("builder", "builder")
@patch('requests.request', return_value=response())
class TestHeaders:

    def test_all_headers_present(self, _, response, builder):
        test_headers = {"testHeader1": "testValue1", "testHeader2": "testValue2"}
        builder.endpoint.response_model.headers = test_headers
        response.header(test_headers)
        try:
            builder.endpoint.get()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_all_headers_absent(self, _, response, builder):
        test_headers = {"testHeader1": "testValue1", "testHeader2": "testValue2"}
        builder.endpoint.response_model.headers = test_headers
        response.header()
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert f"Field 'headers', expected value '{test_headers}', but got '{{}}' " in str(excinfo.value)

    def test_one_header_absent(self, _, response, builder):
        builder.endpoint.response_model.headers = {"testHeader1": "testValue1", "testHeader2": "testValue2"}
        response.header({"testHeader1": "testValue1"})
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert "Field 'headers->testHeader2', expected value 'testValue2', " \
               "but got 'field does not present in response'" in str(excinfo.value)

    def test_multiple_headers_absent(self, _, response, builder):
        builder.endpoint.response_model.headers = {"testHeader1": "testValue1", "testHeader2": "testValue2",
                                                   "testHeader3": "testValue3"}
        response.header({"testHeader1": "testValue1"})
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert "Field 'headers->testHeader2', expected value 'testValue2', " \
               "but got 'field does not present in response' " in str(excinfo.value)
        assert f"Field 'headers->testHeader3', expected value 'testValue3', " \
               f"but got 'field does not present in response'" in str(excinfo.value)

    def test_invalid_header_value(self, _, response, builder):
        test_headers = {"testHeader1": "testValue1"}
        builder.endpoint.response_model.headers = test_headers
        response.header({"testHeader1": "testValue2"})
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert "Field 'headers->testHeader1', expected value 'testValue1', but got 'testValue2' " in str(excinfo.value)

    def test_list_header_valid_value(self, _, response, builder):
        test_headers = {"testHeader1": ["testValue1"]}
        builder.endpoint.response_model.headers = test_headers
        response.header({"testHeader1": ["testValue1"]})
        try:
            builder.endpoint.get()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_list_header_invalid_value(self, _, response, builder):
        test_headers = {"testHeader1": ["testValue1"]}
        builder.endpoint.response_model.headers = test_headers
        response.header({"testHeader1": ["testValue2"]})
        with pytest.raises(RestResponseValidationError) as excinfo:
            builder.endpoint.get()
        assert "Field 'headers->testHeader1->0', expected value 'testValue1', but got 'testValue2'" \
               in str(excinfo.value)


@pytest.mark.usefixtures("builder", "builder")
@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch"])
@patch('requests.request', return_value=response())
class TestBody:

    def test_json_body(self, _, response, builder, method):
        test_body = {"testKey1": "testValue1"}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(test_body)
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_json_body_invalid_value(self, _, response, builder, method):
        test_body = {"testKey1": "testValue1"}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": "testValue2"})
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->testKey1', expected value 'testValue1', but got 'testValue2'" \
               in str(excinfo.value)

    def test_json_body_skip_value(self, _, response, builder, method):
        test_body = {"testKey1": SKIP}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": "testValue2"})
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_json_body_skip_and_invalid_values(self, _, response, builder, method):
        test_body = {"testKey1": SKIP, "testKey2": "testValue2"}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": "testValue1", "testKey2": "testValue1"})
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->testKey2', expected value 'testValue2', but got 'testValue1'" \
               in str(excinfo.value)

    @pytest.mark.parametrize("value", [1, 1.1, "testString", False, True])
    def test_json_body_primitive_values(self, _, response, builder, method, value):
        test_body = {"testKey1": value}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(test_body)
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_json_body_list_valid_value(self, _, response, builder, method):
        test_body = {"testKey1": ["testValue1"]}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(test_body)
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_json_body_list_invalid_value(self, _, response, builder, method):
        test_body = {"testKey1": ["testValue1"]}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": ["testValue2"]})
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->testKey1->0', expected value 'testValue1', but got 'testValue2'" \
               in str(excinfo.value)

    def test_json_body_list_valid_and_invalid_value(self, _, response, builder, method):
        test_body = {"testKey1": ["testValue1", "testValue2"]}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": ["testValue1", "testValue3"]})
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->testKey1->1', expected value 'testValue2', but got 'testValue3'" \
               in str(excinfo.value)

    def test_json_body_list_valid_and_skip_value(self, _, response, builder, method):
        test_body = {"testKey1": ["testValue1", SKIP]}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": ["testValue1", "testValue2"]})
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_json_body_list_invalid_and_skip_value(self, _, response, builder, method):
        test_body = {"testKey1": ["testValue1", SKIP]}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body({"testKey1": ["testValue3", "testValue2"]})
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->testKey1->0', expected value 'testValue1', but got 'testValue3'" \
               in str(excinfo.value)

    def test_json_body_nested_mixed_valid_values(self, _, response, builder, method):
        test_body = {"testKey1": "testValue1",
                     "testKey2": 2,
                     "testKey3": True,
                     "testKey4": [0, 1, "false", False],
                     "testKey5": [
                         {
                             "nestedKey1": "nestedValue1",
                             "nestedKey2": 2,
                             "nestedKey4": [0, 1, "false", False]
                         },
                         {
                             "nested2Key1": "nestedValue1",
                             "nested2Key2": 2,
                             "nested2Key4": [0, 1, "false", False]
                         },
                     ]}
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(test_body)
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_json_body_nested_mixed_valid_invalid_values(self, _, response, builder, method):
        expected_body = {"testKey1": "testValue1",
                         "testKey2": 2,
                         "testKey3": True,
                         "testKey4": [0, 1, "false", False, SKIP],
                         "testKey5": [
                             {
                                 "nestedKey1": "nestedValue1",
                                 "nestedKey2": 2,
                                 "nestedKey4": [0, 1, "false", False]
                             },
                             {
                                 "nested2Key1": "nestedValue1",
                                 "nested2Key2": 2,
                                 "nested2Key3": SKIP,
                                 "nested2Key4": [0, 1, "false", False]
                             },
                         ],
                         "testKey6": SKIP}

        actual_body = {"testKey1": "testValue4",
                       "testKey2": None,
                       "testKey3": False,
                       "testKey4": [0, 2, "true", False, "skippedListValue"],
                       "testKey5": [
                           {
                               "nested2Key1": "nestedValue5",
                               "nested2Key2": 2.2,
                               "nested2Key3": "skippedNestedValue",
                               "nested2Key4": [0, 1.2, "false", "false"]
                           },
                       ],
                       "testKey6": "skippedKeyValue"}

        setattr(builder.endpoint.response_model, f"{method}_data", expected_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(actual_body)
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->testKey1', expected value 'testValue1', but got 'testValue4'" \
               in str(excinfo.value)
        assert f"Field '{method}_data->testKey2', expected value '2', but got 'None'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey3', expected value 'True', but got 'False'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey4->1', expected value '1', but got '2'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey4->2', expected value 'false', but got 'true'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey5->0->nestedKey1', expected value 'nestedValue1', " \
               f"but got 'field does not present in response'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey5->0->nestedKey2', expected value '2', " \
               f"but got 'field does not present in response'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey5->0->nestedKey4', expected value " \
               f"'{expected_body['testKey5'][0]['nestedKey4']}', " \
               f"but got 'field does not present in response'" in str(excinfo.value)
        assert f"Field '{method}_data->testKey5->1', expected value '{expected_body['testKey5']}', " \
               f"but got '{actual_body['testKey5']}'" in str(excinfo.value)

    def test_list_body(self, _, response, builder, method):
        test_body = ["testValue1", "testValue2"]
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(test_body)
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_list_body_invalid_value(self, _, response, builder, method):
        test_body = ["testValue1", "testValue2"]
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(["testValue3", "testValue4"])
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->0', expected value 'testValue1', but got 'testValue3'" in str(excinfo.value)
        assert f"Field '{method}_data->1', expected value 'testValue2', but got 'testValue4'" in str(excinfo.value)

    def test_list_body_skip_value(self, _, response, builder, method):
        test_body = [SKIP, "testValue2"]
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(["testValue3", "testValue2"])
        response.method(method)
        try:
            getattr(builder.endpoint, method)()
        except Exception as e:
            pytest.fail(f"DID RAISE {e}")

    def test_list_body_skip_and_invalid_values(self, _, response, builder, method):
        test_body = [SKIP, "testValue2"]
        setattr(builder.endpoint.response_model, f"{method}_data", test_body)
        builder.endpoint.request_model.allowed_methods = (method,)
        response.body(["testValue2", "testValue1"])
        response.method(method)
        with pytest.raises(RestResponseValidationError) as excinfo:
            getattr(builder.endpoint, method)()
        assert f"Field '{method}_data->1', expected value 'testValue2', but got 'testValue1'" in str(excinfo.value)
