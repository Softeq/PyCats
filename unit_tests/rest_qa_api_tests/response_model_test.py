import pytest

from common.rest_qa_api.base_endpoint import BaseResponseModel
from common.rest_qa_api.rest_exceptions import DataclassNameError, MissingDecoratorError
from common.rest_qa_api.rest_utils import scaf_dataclass
from unit_tests.rest_qa_api_tests.tests_utils import DummyConfigBuilder, DummyApiValidationConfig

response_methods_list = ["status_code", "headers", "get_data", "post_data", "put_data", "patch_data", "delete_data",
                         "error_data", "custom_checkers"]

config = DummyConfigBuilder(DummyApiValidationConfig())


@pytest.mark.parametrize("field_name", response_methods_list)
def test_no_method_impl(field_name):
    with pytest.raises(TypeError) as excinfo:
        list_without_field_name = [x for x in response_methods_list if x != field_name]
        test_response_class = scaf_dataclass(type("_ResponseModel", (BaseResponseModel,),
                                                  dict.fromkeys(list_without_field_name, None)))
        test_response_class()
    assert f"Can't instantiate abstract class _ResponseModel with abstract methods {field_name}" in str(excinfo.value)


def test_all_fields_impl():
    try:
        test_response_class = scaf_dataclass(type("_ResponseModel", (BaseResponseModel,),
                                                  dict.fromkeys(response_methods_list, None)))
        test_response_class(config)
    except Exception as e:
        pytest.fail(f"DID RAISE {e}")


def test_extra_args_no_exception():
    test_response_class = scaf_dataclass(type("_ResponseModel", (BaseResponseModel,),
                                              dict.fromkeys(response_methods_list, None)))
    try:
        test_response_class.test_field = None
        test_response_class(config)
    except Exception as e:
        pytest.fail(f"DID RAISE {e}")


def test_dataclass_name_exception():
    with pytest.raises(DataclassNameError) as excinfo:
        test_response_class = type("ResponseModel", (BaseResponseModel,), dict.fromkeys(response_methods_list, None))
        test_response_class(config)
    assert "Child dataclass should be private. Use _ResponseModel or __ResponseModel instead of ResponseModel" in \
           str(excinfo.value)


def test_missing_decorator_exception():
    with pytest.raises(MissingDecoratorError) as excinfo:
        test_response_class = type("_ResponseModel", (BaseResponseModel,), dict.fromkeys(response_methods_list, None))
        test_response_class(config)
    assert "Child dataclass _ResponseModel should have @scaf_dataclass decorator" in str(excinfo.value)


def test_repr_format():
    test_response_obj = scaf_dataclass(type("_ResponseModel", (BaseResponseModel,),
                                            dict.fromkeys(response_methods_list, "test")))(config)
    assert str(test_response_obj) == "_ResponseModel(custom_checkers=test\ndelete_data" \
                                     "=test\nerror_data=test\n" \
                                     "get_data=test\nheaders=test\npatch_data=test\npost_data=test\nput_data=test\n" \
                                     "raw_response=None\nstatus_code=test)"
