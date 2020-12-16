import copy
import logging
from abc import ABCMeta, abstractmethod
from dataclasses import InitVar
from typing import Any, Dict, Union, Optional, Tuple, Callable, List, Type

from common.config_manager import ConfigManager
from common._rest_qa_api import default_exclude_list, method_exclude_lists
from common._rest_qa_api.response_converter import ResponseConverterMixin
from common._rest_qa_api.response_validator import ResponseValidatorMixin
from common._rest_qa_api.rest_exceptions import MethodNotSupportedByEndpoint, DataclassNameError, \
    RestResponseValidationError, MissingDecoratorError
from common._rest_qa_api.rest_utils import pycats_dataclass, make_request_url, dict_to_obj, obj_to_dict

import requests

logger = logging.getLogger(__name__)


@pycats_dataclass(repr=True, eq=True)
class BaseRequestModel(metaclass=ABCMeta):
    """Abstract Base class for HTTP request model description.

    Developed according to standard python dataclass:
    https://docs.python.org/3/library/dataclasses.html

    Instead of default python @dataclass decorator, own decorator @pycats_dataclass is used.
    The goal for this is to prevent __repr__ and __eq__ methods generation by default, make typing is optional,
    and support mutable fields without extra syntax.

    Child classes should implement all abstract properties defined in this class
    See the property's description in the property's getter method.

    Examples:
        from common._rest_qa_api.base_endpoint import BaseRequestModel
        from common._rest_qa_api.rest_utils import SKIP, pycats_dataclass

        @pycats_dataclass
        class _TestEndpointRequestModel(BaseRequestModel):
            resource = '/test'
            headers = {"Content-Type": "application/json"}
            post_data = None
            put_data = None
            patch_data = None
            delete_data = None
            params = "_format=json"
            allowed_methods = ("get",)
    """

    def __new__(cls, *args, **kwargs):
        """Overrides __new__ to verify child class named in private and pycats_dataclass decorator is used
        Returns:
            object: BaseRequestModel object
        Raises:
            DataclassNameError if child class not started with '_'
            MissingDecoratorError if child class not used pycats_dataclass decorator
        """
        if not cls.__name__.startswith("_"):
            raise DataclassNameError(cls.__name__)
        if not cls.__dict__.get("__annotations__"):
            raise MissingDecoratorError(cls.__name__)
        return super().__new__(cls)

    _resource: str = None
    _headers: Any = None
    _post_data: Any = None
    _put_data: Any = None
    _patch_data: Any = None
    _delete_data: Any = None
    _params: str = None
    _allowed_methods: Tuple = None

    @property
    @abstractmethod
    def resource(self) -> str:
        """str: HTTP resource part. Example: /campaigns/1/actions/send

        Returns:
            :str HTTP resource
        """
        return self.resource

    @resource.setter
    @abstractmethod
    def resource(self, value):
        self._resource = value

    @property
    @abstractmethod
    def headers(self) -> Optional[dict]:
        """dict: HTTP headers. Example: {"Content-Type": "application/json"}

        Returns:
            :Optional[dict] Request headers
        """
        return self._headers

    @headers.setter
    @abstractmethod
    def headers(self, headers) -> None:
        self._headers = headers

    @property
    @abstractmethod
    def post_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: HTTP post body data.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]]  Post body
        """
        return self._post_data

    @post_data.setter
    @abstractmethod
    def post_data(self, post_data) -> None:
        self._post_data = post_data

    @property
    @abstractmethod
    def put_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: HTTP put body data.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]]  Put body
        """
        return self._put_data

    @put_data.setter
    @abstractmethod
    def put_data(self, put_data) -> None:
        self._put_data = put_data

    @property
    @abstractmethod
    def patch_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: HTTP patch body data.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Patch body
        """
        return self._patch_data

    @patch_data.setter
    @abstractmethod
    def patch_data(self, patch_data) -> None:
        self._patch_data = patch_data

    @property
    @abstractmethod
    def delete_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: HTTP delete body data.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Delete body
        """
        return self._delete_data

    @delete_data.setter
    @abstractmethod
    def delete_data(self, delete_data) -> Any:
        self._delete_data = delete_data

    @property
    @abstractmethod
    def params(self) -> str:
        """Optional[str]: HTTP params to specify in URL

        Returns:
            :Optional[Union[dict, str]] HTTP params
        """
        return self._params

    @params.setter
    @abstractmethod
    def params(self, params) -> None:
        self._params = params

    @property
    @abstractmethod
    def allowed_methods(self) -> Tuple:
        """Optional[Tuple]: allowed HTTP methods for this resource

        Returns:
            :tuple Allowed HTTP methods for resource
        """
        return self._allowed_methods

    @allowed_methods.setter
    @abstractmethod
    def allowed_methods(self, allowed_methods) -> None:
        self._allowed_methods = allowed_methods


@pycats_dataclass(repr=True, eq=False)
class BaseResponseModel(ResponseConverterMixin, ResponseValidatorMixin, metaclass=ABCMeta):
    """Abstract Base class for HTTP Response model description.

    ResponseConverterMixin is used to convert HTTP response to the model format.

    ResponseValidatorMixin is used to verify the HTTP response matches the expected model
    using the __eq__ method. Detailed information see in ResponseValidatorMixin docstring.
    It also executes the checkers from self.custom_checkers list where custom validators may be located.

    The Response body is verified based on the HTTP Request Method used: if the request method is GET,
    field get_data will be used to verify response body

    Custom syntax format introduced:

        Use .rest_utils.SKIP class as value to exclude field or part of the structure from validation
        Use 'None' - as expected empty or null value
        Use primitive values for validation: str, bool, int

    Developed according to standard python dataclass: https://docs.python.org/3/library/dataclasses.html

    Instead of default python @dataclass decorator, own decorator @pycats_dataclass is used.
    The goal for this is to prevent __repr__ and __eq__ methods generation by default, make typing is optional,
    and support mutable fields without extra syntax.

    Child classes should implement all abstract properties defined in this class
    See the property's description in the property's getter method.

    Args:
        raw_response (Response): Populated automatically after Response received

    Examples:
        from common._rest_qa_api.base_endpoint import BaseResponseModel
        from common._rest_qa_api.rest_utils import SKIP, pycats_dataclass

        @pycats_dataclass
        class _TestEndpointResponseModel(BaseResponseModel):
            status_code: int = 200
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            get_data = {'url_link': None,
                        'users': [
                                {"id": "1", "album_id": "2340"},
                                SKIP,
                                SKIP,
                                {"id": "4", "album_id": "2351"}
                        ]}
            post_data = None
            put_data = None
            delete_data = None
            patch_data = None
            error_data = {'error': 'Error Code', 'message': 'Error Message'}
            custom_checkers = []

      During the Response handling for the GET request the following checks will be performed:
          1) status_code field value is 200
          2) Content-Type header has value 'application/json; charset=utf-8'
          3) url_link in the body is empty
          4) Only users 1 and 4 will be verified. Verification for 2,3,5,etc will be SKIPPED

      For POST, PUT, DELETE, PATCH request methods empty response value will be expected.
      In case of invalid status code the response will be tried to validated according to error_data field

      Custom Validation Logic:
          If you want to add custom validation to your response and skip default model validation,
          you can mark fields or value as SKIP and add your callable object to the custom_checkers list.

          In the example above self.custom_checkers initialized as an empty list to be filled in during runtime,
          but you can also predefine the list of necessary functions to call.
    """

    def __new__(cls, *args, **kwargs):
        """Overrides __new__ to verify child class named is private and pycats_dataclass decorator is used

        Returns:
            object: BaseResponseModel object

        Raises:
            DataclassNameError if child class not started with '_'
            MissingDecoratorError if child class not used pycats_dataclass decorator
        """
        if not cls.__name__.startswith("_"):
            raise DataclassNameError(cls.__name__)
        if not cls.__dict__.get("__annotations__"):
            raise MissingDecoratorError(cls.__name__)
        return super().__new__(cls)

    config: InitVar[ConfigManager]
    _status_code: int = None
    _get_data: Any = None
    _post_data: Any = None
    _put_data: Any = None
    _patch_data: Any = None
    _delete_data: Any = None
    _error_data: Any = None
    _headers: Dict = None
    _custom_checkers = []
    # Used to keep original requests.Response() object
    raw_response: requests.Response = None

    @property
    @abstractmethod
    def status_code(self) -> int:
        """int: Expected HTTP Status code

        Returns:
            :int Expected status code
        """
        return self._status_code

    @status_code.setter
    @abstractmethod
    def status_code(self, status_code: int) -> None:
        self._status_code = status_code

    @property
    @abstractmethod
    def get_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: Expected HTTP body for GET method.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Expected response body
        """
        return self._get_data

    @get_data.setter
    @abstractmethod
    def get_data(self, get_data) -> None:
        self._get_data = get_data

    @property
    @abstractmethod
    def post_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: Expected HTTP body for POST method.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Expected response body
        """
        return self._post_data

    @post_data.setter
    @abstractmethod
    def post_data(self, post_data) -> None:
        self._post_data = post_data

    @property
    @abstractmethod
    def put_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: Expected HTTP body for PUT method.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Expected response body
        """
        return self._put_data

    @put_data.setter
    @abstractmethod
    def put_data(self, put_data) -> None:
        self._put_data = put_data

    @property
    @abstractmethod
    def patch_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: Expected HTTP body for PATCH method.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Expected response body
        """
        return self._patch_data

    @patch_data.setter
    @abstractmethod
    def patch_data(self, patch_data) -> None:
        self._patch_data = patch_data

    @property
    @abstractmethod
    def delete_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: Expected HTTP body for DELETE method.
        May be dict/str/binary type

        Returns:
            :Optional[Union[dict, str]] Expected response body
        """
        return self._delete_data

    @delete_data.setter
    @abstractmethod
    def delete_data(self, delete_data) -> None:
        self._delete_data = delete_data

    @property
    @abstractmethod
    def error_data(self) -> Optional[Union[dict, str]]:
        """Optional[Union[dict, str]]: Expected HTTP response format for errors.
        May be dict/str/binary type.

        Example: {'error': 'Error Code', 'message': 'Error Message'}

        Returns:
            :Optional[Union[dict, str]] Expected error response body format
        """
        return self._error_data

    @error_data.setter
    @abstractmethod
    def error_data(self, error_data) -> None:
        self._error_data = error_data

    @property
    @abstractmethod
    def headers(self) -> Optional[dict]:
        """Optional[dict]: Expected HTTP Response headers.

         Example: {"Content-Type": "application/json"}

        Returns:
            :Optional[dict] Expected Response headers
        """
        return self._headers

    @headers.setter
    @abstractmethod
    def headers(self, headers) -> None:
        self._headers = headers

    @property
    @abstractmethod
    def custom_checkers(self) -> Optional[List]:
        """Optional[List]: List of custom checkers to be run during the validation

        Returns:
            :Optional[List] List of checkers
        """
        return self._custom_checkers

    @custom_checkers.setter
    @abstractmethod
    def custom_checkers(self, custom_checkers) -> None:
        self._custom_checkers = custom_checkers

    def __post_init__(self, config: ConfigManager):
        super().__init__(config.get_api_validations())

    def __repr__(self):
        """Override __repr__ to support custom class representation

        Returns:
            :str with class name and all public properties
        """
        return f"{self.__class__.__qualname__}" + f"(" + \
               "\n".join(f"{f}={self.__getattribute__(f)}"
                         for f in [field for field in dir(self) if
                                   not callable(getattr(self, field)) and not field.startswith("_")]) + f")"


class BaseEndpoint:
    def __init__(self, base_url: str, request_model: BaseRequestModel,
                 response_model: BaseResponseModel, make_url_method):
        """Class representation for the agent and container for HTTP Request/Response models

        Takes request model, parses it and sends to request library,
        provides __getattr__ to allow calls only from request_model.allowed_methods tuple.
        Converts raw response to Model format and performs validation based on the Model.


        Examples:

            >>> class TestEndpoint(BaseEndpoint):
                    def __init__(self, base_url):
                        # _TestEndpointRequestModel should be implementation of BaseRequestModel
                        self.request_model = _TestEndpointRequestModel()
                        # _TestEndpointResponseModel should be implementation of BaseResponseModel
                        self.response_data = _TestEndpointResponseModel()
                        self.base_url = base_url

                        super().__init__(self.base_url, self.request_model, self.response_data, make_request_url)

        Attributes:
            base_url (str): Base part of the HTTP URL. E.x: https://google.com/api/v1/
            request_model (BaseRequestModel): Instance of BaseRequestModel
            response_model (BaseResponseModel): Instance of  BaseResponseModel
            make_url_method (object): collable object to format the URL based on the base_url and
                resource from BaseRequestModel.resource
        """
        self.base_url = base_url
        self.request_model = request_model
        self.response_model = response_model
        self.make_url_method = make_url_method
        # Dummy container to prepare request fields
        self._request = type("Jon_Galt", (object,), dict())()

    def __getattr__(self, item):
        """Verifies if the called method presents in self.request_model.allowed_methods

        Args:
            item (str): method name to call

        Returns:
            :BaseResponseModel - requests.Response object converted to BaseResponseModel class

        Raises:
            MethodNotSupportedByEndpoint if method not in allowed list
        """
        if not item.startswith("__") and item not in self.request_model.allowed_methods:
            raise MethodNotSupportedByEndpoint(item)
        else:
            return lambda: self.execute(item)

    def __request_builder(self, method):
        value = obj_to_dict(self._request, exclude_params=default_exclude_list + method_exclude_lists[method])
        if method == "get":
            return value
        # JSON supports 2 formats - dict and list
        if isinstance(value[f"{method}_data"], dict) or isinstance(value[f"{method}_data"], list):
            value["json"] = value.pop(f"{method}_data")
        else:
            value["data"] = value.pop(f"{method}_data")
        return value

    def execute(self, method: str, base_validation=True):
        """Main method to send the request and perform response conversion and validation

        Args:
            method (str): HTTP method to use. E.x: post, get, etc
            base_validation (bool): If True - performs validation, otherwise skip it

        Returns:
            :BaseResponseModel object with response data

        Raises:
            :RestResponseValidationError if __eq__ returns false
        """
        dict_to_obj(self._request, method=method, base_url=self.base_url, **obj_to_dict(self.request_model))
        self.make_url_method(self._request)
        result = requests.request(**self.__request_builder(method))
        response = self.response_model.convert_raw_response(result)
        if base_validation and not response == self.response_model:
            raise RestResponseValidationError(response)
        return response


def endpoint_factory(base_url: str, class_name: str, request_model: Type[BaseRequestModel],
                     response_model: Type[BaseResponseModel], superclass=BaseEndpoint,
                     make_url_method=make_request_url, config=None) \
        -> Union[Callable[[], BaseEndpoint], BaseEndpoint]:
    """Factory to create class based on BaseEndpoint

    Attributes:
        base_url (str): Base part of the HTTP URL. E.x: https://example.com/api/v1/
        class_name (str): Class name will be assigned to created class
        request_model (BaseRequestModel impl): Child of BaseRequestModel
        response_model (BaseResponseModel impl):  Child of BaseResponseModel
        superclass (BaseEndpoint): Base class for inheritance. BaseEndpoint by default
        make_url_method (object): collable object for format the URL based on the base_url and
                resource from BaseRequestModel.resource

    Returns:
        :obj lambda with class which 'class_name' is inherited from 'superclass'
    """
    if not config:
        config = ConfigManager()
    dummy_class = type(class_name, (superclass,), dict(request_model=None, response_model=None, base_url=None,
                                                       make_url_method=None))
    return lambda: dummy_class(base_url, request_model=copy.deepcopy(request_model()),
                               response_model=copy.deepcopy(response_model(config=config)),
                               make_url_method=make_url_method)
