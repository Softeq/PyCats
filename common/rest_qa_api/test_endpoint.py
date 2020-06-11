from common.rest_qa_api.base_endpoint import BaseRequestModel, BaseResponseModel, endpoint_factory
from common.rest_qa_api.rest_utils import SKIP, scaf_dataclass
from common.rest_qa_api.rest_checkers import check_json_structure, check_status, JSONCheckers

base_url = 'https://gorest.co.in/public-api'


@scaf_dataclass
class TestEndpointBuilder:

    @scaf_dataclass
    class _TestEndpointRequestModel(BaseRequestModel):
        resource = '/photos'
        headers = {"Content-Type": "application/json"}
        post_data = None
        put_data = None
        patch_data = None
        delete_data = None
        params = "_format=json&access-token=uwikLcxUWu4jHOIGcqKLXf2NzLxvPB0xyqCf"
        allowed_methods = ("get",)

    @scaf_dataclass
    class _TestEndpointResponseModel(BaseResponseModel):
        status_code = 200
        headers = {'Content-Type': 'application/json; charset=UTF-8', 'ETag': '"5bf84e22-ad38-466e-ad94-63ee4b89a168"'}
        get_data = {"_meta": {"success": True, "code": 200,
                              "message": "OK. Everything worked as expected.",
                              "totalCount": SKIP,
                              "pageCount": SKIP,
                              "currentPage": 1,
                              "perPage": 20,
                              "rateLimit": {"limit": 30, "remaining": 29, "reset": 2}},
                    "result": [
                        {"id": "1", "album_id": "2793", "title": "Velit aut soluta qui "
                                                                 "minima inventore aut est. "
                                                                 "Quod consectetur provident "
                                                                 "minus.",
                         "url": "https://lorempixel.com/1024/768/abstract/?43521",
                         "thumbnail": "https://lorempixel.com/150/150/abstract/?50028",
                         "_links": {
                             "self": {"href": "https://gorest.co.in/public-api/photos/1"},
                             "edit": {"href": "https://gorest.co.in/public-api/photos/1"}}},
                        SKIP,
                        SKIP,
                        {"id": "4", "album_id": "2653",
                         "title": "Eveniet est laborum nesciunt odit quasi quo dolor. Ut "
                                  "possimus consequatur architecto sapiente.",
                         "url": "https://lorempixel.com/1024/768/abstract/?16952",
                         "thumbnail": "https://lorempixel.com/150/150/abstract/?25591",
                         "_links": {
                             "self": {"href": "https://gorest.co.in/public-api/photos/4"},
                             "edit": {"href": "https://gorest.co.in/public-api/photos/4"}}},
                    ]}
        post_data = None
        put_data = None
        delete_data = None
        patch_data = None
        error_data = None
        custom_checkers = []

    endpoint = endpoint_factory(base_url, "TestEndpoint", _TestEndpointRequestModel, _TestEndpointResponseModel)

    def get_photos(self):
        response = self.endpoint.get()
        return response.get_data


test_endpoint = TestEndpointBuilder()
JSONCheckers.deactivate(JSONCheckers.check_status)
JSONCheckers.expected_json_structure = {"fake_field": "fake_value"}
test_endpoint.endpoint.response_model.custom_checkers.append(JSONCheckers)
test_endpoint.endpoint.response_model.custom_checkers.append(check_json_structure({"fake_field": "fake_value"}))
test_endpoint.endpoint.response_model.custom_checkers.append(check_status(205))
result = test_endpoint.get_photos()
