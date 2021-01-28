import json
import pytest

from common._rest_qa_api.base_endpoint import ResponseConverterMixin
from unit_tests.rest_qa_api_tests.tests_utils import DummyResponseBuilder, TestEndpointBuilder, \
    exclude_fields_from_obj, DummyConfigBuilder, DummyApiValidationConfig

affected_fields_get = ("raw_response", "status_code", "headers", "get_data")
affected_fields_error = ("raw_response", "status_code", "headers", "error_data")

config = DummyConfigBuilder(DummyApiValidationConfig())


def test_status_code_converter():
    orig_response = DummyResponseBuilder().method().code(500).body()
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.status_code == orig_response.status_code


def test_headers_converter():
    orig_response = DummyResponseBuilder().method().code().body()
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.headers == orig_response.headers


def test_body_json_converter_valid_value():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code().header({"Content-Type": "application/json"}).body(
        json.dumps(test_body))
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.get_data == test_body


def test_body_json_converter_not_json_mime_type():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code().header({"Content-Type": "text/plain"}).body(
        json.dumps(test_body))
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.get_data == json.dumps(test_body)


def test_body_json_converter_no_mime_type_provided():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code().body(json.dumps(test_body))
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.get_data == json.dumps(test_body)


def test_body_json_converter_invalid_body():
    test_body = "testField = testValue"
    orig_response = DummyResponseBuilder().method().code().header({"Content-Type": "application/json"}).body(test_body)
    with pytest.raises(TypeError) as excinfo:
        ResponseConverterMixin().convert_raw_response(orig_response)
    assert f"Incorrect json format: {test_body}" in str(excinfo.value)


def test_body_json_converter_error_status_code():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code(500).body(json.dumps(test_body))
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.error_data == json.dumps(test_body)


def test_converter_raw_response():
    orig_response = DummyResponseBuilder().method().code(500).body("asd: asd").header({"Content-Type": "text/plain"})
    converted_response = ResponseConverterMixin().convert_raw_response(orig_response)
    assert converted_response.raw_response == orig_response


def test_status_code_converter_as_mixin():
    orig_response = DummyResponseBuilder().method().code(500).body()
    converted_response = TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert converted_response.status_code == orig_response.status_code
    assert exclude_fields_from_obj(converted_response, affected_fields_error) == \
        exclude_fields_from_obj(TestEndpointBuilder._TestResponseModel(config), affected_fields_error)


def test_headers_converter_as_mixin():
    orig_response = DummyResponseBuilder().method().code().body()
    converted_response = TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert converted_response.headers == orig_response.headers
    assert exclude_fields_from_obj(converted_response, affected_fields_get) == \
        exclude_fields_from_obj(TestEndpointBuilder._TestResponseModel(config), affected_fields_get)


def test_body_json_converter_as_mixin_valid_value():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code().header({"Content-Type": "application/json"}).body(
        json.dumps(test_body))
    converted_response = TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert converted_response.get_data == test_body
    assert exclude_fields_from_obj(converted_response, affected_fields_get) == \
        exclude_fields_from_obj(TestEndpointBuilder._TestResponseModel(config), affected_fields_get)


def test_body_json_converter_as_mixin_not_json_mime_type():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code().header({"Content-Type": "text/plain"}).body(
        json.dumps(test_body))
    converted_response = TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert converted_response.get_data == json.dumps(test_body)
    assert exclude_fields_from_obj(converted_response, affected_fields_get) == \
        exclude_fields_from_obj(TestEndpointBuilder._TestResponseModel(config), affected_fields_get)


def test_body_json_converter_as_mixin_no_mime_type_provided():
    test_body = {"testField": "testValue"}
    orig_response = DummyResponseBuilder().method().code().body(
        json.dumps(test_body))
    converted_response = TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert converted_response.get_data == json.dumps(test_body)
    assert exclude_fields_from_obj(converted_response, affected_fields_get) == \
        exclude_fields_from_obj(TestEndpointBuilder._TestResponseModel(config), affected_fields_get)


def test_body_json_converter_as_mixin_invalid_body():
    test_body = "testField = testValue"
    orig_response = DummyResponseBuilder().method().code().header({"Content-Type": "application/json"}).body(test_body)
    with pytest.raises(TypeError) as excinfo:
        TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert f"Incorrect json format: {test_body}" in str(excinfo.value)


def test_body_json_converter_as_mixin_error_status_code():
    test_body = "testField = testValue"
    orig_response = DummyResponseBuilder().method().code(500).body(test_body)
    converted_response = TestEndpointBuilder._TestResponseModel(config).convert_raw_response(orig_response)
    assert converted_response.error_data == test_body
    assert exclude_fields_from_obj(converted_response, affected_fields_error) == \
        exclude_fields_from_obj(TestEndpointBuilder._TestResponseModel(config), affected_fields_error)
