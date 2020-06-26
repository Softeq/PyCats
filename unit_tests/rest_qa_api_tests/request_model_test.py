import pytest

from common.rest_qa_api.base_endpoint import BaseRequestModel
from common.rest_qa_api.rest_exceptions import DataclassNameError, MissingDecoratorError
from common.rest_qa_api.rest_utils import scaf_dataclass

request_methods_list = ["resource", "headers", "post_data", "put_data", "patch_data", "delete_data",
                        "params", "allowed_methods"]


@pytest.mark.parametrize("field_name", request_methods_list)
def test_no_field_impl(field_name):
    with pytest.raises(TypeError) as excinfo:
        list_without_field_name = [x for x in request_methods_list if x != field_name]
        test_request_class = scaf_dataclass(type("_RequestModel", (BaseRequestModel,),
                                                 dict.fromkeys(list_without_field_name, None)))
        test_request_class()
    assert f"Can't instantiate abstract class _RequestModel with abstract methods {field_name}" in str(excinfo.value)


def test_all_fields_impl():
    try:
        test_request_class = scaf_dataclass(type("_RequestModel", (BaseRequestModel,),
                                                 dict.fromkeys(request_methods_list, None)))
        test_request_class()
    except Exception as e:
        pytest.fail(f"DID RAISE {e}")


def test_extra_args_no_exception():
    test_request_class = scaf_dataclass(type("_RequestModel", (BaseRequestModel,),
                                             dict.fromkeys(request_methods_list, None)))
    try:
        test_request_class.test_field = None
        test_request_class()
    except Exception as e:
        pytest.fail(f"DID RAISE {e}")


def test_dataclass_name_exception():
    with pytest.raises(DataclassNameError) as excinfo:
        test_request_class = type("RequestModel", (BaseRequestModel,), dict.fromkeys(request_methods_list, None))
        test_request_class()
    assert "Child dataclass should be private. Use _RequestModel or __RequestModel instead of RequestModel" in \
           str(excinfo.value)


def test_missing_decorator_exception():
    with pytest.raises(MissingDecoratorError) as excinfo:
        test_request_class = type("_RequestModel", (BaseRequestModel,), dict.fromkeys(request_methods_list, None))
        test_request_class()
    assert "Child dataclass _RequestModel should have @scaf_dataclass decorator" in str(excinfo.value)
