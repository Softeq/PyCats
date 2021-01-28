import json
from copy import deepcopy
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    # to avoid import loop only for annotations
    from common._rest_qa_api.base_endpoint import BaseResponseModel  # noqa
    from common._rest_qa_api.response_validator import ResponseValidatorMixin  # noqa


class ResponseConverterMixin:
    """Mixin to convert :requests.Response() object to PyCats response model
    Converts status_code, headers, body to the model format
    Assigns response object to self.raw_response field
    If HTTP response status is not ok - populates error_data field by response data
    """

    def convert_raw_response(self: Union['BaseResponseModel', 'ResponseConverterMixin', 'ResponseValidatorMixin'],
                             response):
        response_container = deepcopy(self)
        response_container.raw_response = response
        self._convert_status(response_container)
        self._convert_header(response_container)
        self._convert_body(response_container)
        return response_container

    def _convert_body(self, response_container):
        if not response_container.raw_response.ok:
            # set model body to model.error_data
            self._set_body_value('error_data', response_container)
        else:
            # set model body based on the request method
            self._set_body_value(f'{response_container.raw_response.request.method.lower()}_data', response_container)

    @staticmethod
    def _set_body_value(field, response_container):
        # get response body (text field)
        response_body = response_container.raw_response.text
        # determine data format in response to convert it to dict ot use raw text
        response_content_type = response_container.raw_response.headers.get('Content-Type')
        if response_content_type and 'application/json' in response_content_type:
            try:
                setattr(response_container, field, json.loads(response_body))
            except json.JSONDecodeError:
                raise TypeError(f'Incorrect json format: {response_body}')
        else:
            setattr(response_container, field, response_body)

    @staticmethod
    def _convert_header(response_container):
        response_container.headers = dict(response_container.raw_response.headers)

    @staticmethod
    def _convert_status(response_container):
        response_container.status_code = response_container.raw_response.status_code
