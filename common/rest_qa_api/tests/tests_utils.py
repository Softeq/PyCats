from requests import Response, Request

from common.libs.helpers.singleton import Singleton
from common.rest_qa_api.base_endpoint import BaseRequestModel, BaseResponseModel, endpoint_factory
from common.rest_qa_api.rest_utils import scaf_dataclass, SKIP


@scaf_dataclass
class TestEndpointBuilder:

    @scaf_dataclass
    class _TestRequestModel(BaseRequestModel):
        resource = ""
        headers = None
        post_data = None
        put_data = None
        patch_data = None
        delete_data = None
        params = None
        allowed_methods = None

    @scaf_dataclass
    class _TestResponseModel(BaseResponseModel):
        status_code = SKIP
        headers = SKIP
        get_data = SKIP
        post_data = SKIP
        put_data = SKIP
        delete_data = SKIP
        patch_data = SKIP
        error_data = SKIP
        custom_checkers = None

    endpoint = endpoint_factory("", "Dummy", _TestRequestModel, _TestResponseModel)


class DummyResponseBuilder(Response, metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.request = Request()

    def code(self, status_code=200):
        self.status_code = status_code
        return self

    def method(self, method="get"):
        self.request.method = method
        return self

    def header(self, headers=dict()):
        self.headers = headers
        return self

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, body):
        self._text = body

    def body(self, body=""):
        self.text = body
        return self

    def set_default_state(self):
        self.method().code().header({}).body()


def exclude_fields_from_obj(obj, affected_fields):
    return {key: value for key, value in obj.__dict__.items() if key not in affected_fields}