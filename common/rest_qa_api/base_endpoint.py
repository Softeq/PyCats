import json
import inspect
from copy import deepcopy, copy
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Union, Optional, Tuple, Callable, List, Type

from common import scaf
from common.rest_qa_api import default_exclude_list, method_exclude_lists
from common.rest_qa_api.rest_checkers import BaseRESTCheckers
from common.rest_qa_api.rest_exceptions import MethodNotSupportedByEndpoint, DataclassNameError, \
    RestResponseValidationError
from common.rest_qa_api.rest_utils import scaf_dataclass, make_request_url, dict_to_obj, obj_to_dict
from common.rest_qa_api.rest_utils import SKIP

from requests import Response, request

logger = scaf.get_logger(__name__)


class ResponseValidatorMixin:
    """
    Mixin to provide a mechanism to compare the response model with the actual response.
    Validation is archived using the __eq__ method override.

    Because self contains the response in BaseResponseModel format we compare it with the provided model.
    During the verification, all errors are saved in self.errors.
    2 types of validations are supported: default validation according to the model and custom user checkers.

    The default validation rulse are initialized based on the config values. It is possible to override them for each
    endpoint separately.
    It is also possible to provide additional custom checkers by adding them to the custom_checkers list.
    """

    _check_status_code = scaf.config.api_settings.api_validation_settings.validate_status_code
    _check_headers = scaf.config.api_settings.api_validation_settings.validate_headers
    _check_body = scaf.config.api_settings.api_validation_settings.validate_body
    _fail_if_field_is_missing = scaf.config.api_settings.api_validation_settings.fail_if_field_is_missing

    @classmethod
    def configure_validator(cls, validate_status_code=True, validate_headers=True, validate_body=True,
                            fail_if_field_is_missing=True):
        """Performs default validators setup for endpoint if default values should be override.

        Args:
            validate_status_code (bool): Performs status code validation if True
            validate_headers (bool): Performs headers validation if True
            validate_body (bool): Performs body validation if True
            fail_if_field_is_missing (bool): Fail validation if some field from model is absent in response.
            Added for cases when response may contain only part of model's values and it is expected.

        """
        cls._check_status_code = validate_status_code
        cls._check_headers = validate_headers
        cls._check_body = validate_body
        cls._fail_if_field_is_missing = fail_if_field_is_missing

    def __eq__(self: Union['BaseResponseModel', 'ResponseConverterMixin', 'ResponseValidatorMixin'], model):
        """Performs object fields comparison.

        Validates:
            1) response status code
            2) headers
            3) body

        Method extracts HTTP method used in Request and use the appropriate field from response and model for validation
        Recursively validates all fields in JSON structure.
        Calls functions/objects from the custom_checker list if provided.
        For each fail case appends error in self.errors list.

        Args:
            model (BaseResponseModel): BaseResponseModel instance with model for validation

        Returns:
            True if validation passed, otherwise returns False

        """
        self.errors = {"default": [], "custom": []}
        # Need to keep recursion depth and store the json fields
        self.field_nesting = []

        if not isinstance(self, model.__class__):
            return False

        if not self.raw_response.ok:
            property_name = "error_data"
        else:
            property_name = f'{self.raw_response.request.method.lower()}_data'
        body_to_verify = getattr(self, f'{property_name}')
        model_data = getattr(model, property_name)

        # Verify basic validation rules and perform response validation
        if self._check_status_code:
            self._validate_structure('status_code', self.status_code, model.status_code)
        if self._check_body:
            self._validate_structure(property_name, body_to_verify, model_data)
        if self._check_headers:
            self._validate_structure('headers', self.headers, model.headers)
        if self.custom_checkers:
            self._run_checkers()
        if self.errors["default"] or self.errors["custom"]:
            return False
        return True

    def _validate_structure(self, field_name, data_to_verify, model_to_verify, list_position=None):
        """Recursively validates provided data_to_verify based on the model_to_verify

        If value is SKIP - exits from function
        If value is instance of dict - calls itself for each key
        If value is instance of list - calls itself for each element in list
        If value is custom object or primitive data type - asserts data with model using native __eq__

        In case if assertion fails - append error with field name to self.errors["default"] list

        Args:
            field_name (str): Field name to validated
            data_to_verify (Any): Data to verify
            model_to_verify (Any): Model to verify the data
        """
        if list_position is None:
            self.field_nesting.append(field_name)

        if model_to_verify == SKIP:
            if list_position is None:
                self.field_nesting.pop()
            return

        if isinstance(data_to_verify, dict):
            # if for cases when model or data is empty dict
            if model_to_verify and data_to_verify:
                for key, value in model_to_verify.items():
                    try:
                        self._validate_structure(key, data_to_verify[key], model_to_verify[key])
                    except KeyError:
                        # for case when key is absent in response. If _fail_if_field_is_missing is False
                        # logs warning message
                        if self._fail_if_field_is_missing:
                            self.field_nesting.append(key)
                            self.errors["default"].append((copy(self.field_nesting), model_to_verify[key],
                                                           "field does not present in response"))
                        else:
                            logger.warning(f"The field {key} is not present in response. Please verify your model")
            else:
                self.errors["default"].append((copy(self.field_nesting), model_to_verify, data_to_verify))

        elif isinstance(data_to_verify, list):
            # if for cases when model or data is empty list
            if model_to_verify and data_to_verify:
                for number, item in enumerate(model_to_verify):
                    # add element position in list
                    self.field_nesting.append(number)
                    self._validate_structure(field_name, data_to_verify[number], model_to_verify[number], number)
                    self.field_nesting.pop()
            else:
                self.errors["default"].append((copy(self.field_nesting), model_to_verify, data_to_verify))
        else:
            if not model_to_verify == data_to_verify:
                self.errors["default"].append((copy(self.field_nesting), model_to_verify, data_to_verify))
        if list_position is None:
            self.field_nesting.pop()

    def _run_checkers(self: Union['BaseResponseModel', 'ResponseValidatorMixin']):
        """Executes all provided checkers in loop

        Supports 2 types of checkers - class inherited from BaseRESTCheckers class and functions.
        In case of custom check errors adds them to self.errors["custom"]
        """
        for checker in self.custom_checkers:
            logger.info(f"run checker: {checker.__name__}: ")
            try:
                if inspect.isfunction(checker):
                    checker(self)
                elif isinstance(checker(), BaseRESTCheckers):
                    errors = checker.execute(self)
                    self.errors["custom"] = errors
                else:
                    raise TypeError(f'{checker} has unsupported type. Supported are functions and '
                                    f'BaseRESTCheckers instances')
            except AssertionError as err:
                self.errors["custom"].append((checker, err))
            except Exception as err:
                logger.info("fail")
                logger.exception(err)
                raise
            else:
                logger.info(f"{checker.__name__} validation passed")


@scaf_dataclass(repr=True, eq=True)
class BaseRequestModel(metaclass=ABCMeta):
    """Abstract Base class for HTTP request model description.

    Developed according to standard python dataclass:
    https://docs.python.org/3/library/dataclasses.html

    Instead of default python @dataclass decorator, own decorator @scaf_dataclass is used.
    The goal for this is to prevent __repr__ and __eq__ methods generation by default, make typing is optional,
    and support mutable fields without extra syntax.

    Child classes should implement all abstract properties defined in this class
    See the property's description in the property's getter method.

    Examples:
        from common.rest_qa_api.base_endpoint import BaseRequestModel
        from common.rest_qa_api.rest_utils import SKIP, scaf_dataclass

        @scaf_dataclass
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


class ResponseConverterMixin:
    """Mixin to convert :requests.Response() object to SCAF response model

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


@scaf_dataclass(repr=True, eq=False, init=False)
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

    Instead of default python @dataclass decorator, own decorator @scaf_dataclass is used.
    The goal for this is to prevent __repr__ and __eq__ methods generation by default, make typing is optional,
    and support mutable fields without extra syntax.

    Child classes should implement all abstract properties defined in this class
    See the property's description in the property's getter method.

    Args:
        raw_response (Response): Populated automatically after Response received

    Examples:
        from common.rest_qa_api.base_endpoint import BaseResponseModel
        from common.rest_qa_api.rest_utils import SKIP, scaf_dataclass

        @scaf_dataclass
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
        """Overrides __new__ to verify child class named as private

        Returns:
            object: BaseResponseModel object

        Raises:
            DataclassNameError if child class not started with '_'
        """
        if not cls.__name__.startswith("_"):
            raise DataclassNameError(cls.__name__)
        return super().__new__(cls)

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
    raw_response: Response = None

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
    def status_code(self, status_code) -> None:
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

    def __repr__(self):
        """Override __repr__ to support custom class representation

        Returns:
            :str with class name and all public properties
        """
        return f"{self.__class__.__qualname__}" + f"(" + \
               "\n".join(f"{f}={self.__getattribute__(f)}"
                         for f in [field for field in dir(self) if
                                   not callable(getattr(self, field))
                                   and not field.startswith("_")]) + f")"


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
        self._request = type("Jon_Golt", (object,), dict())()

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
        if isinstance(value[f"{method}_data"], dict) or isinstance(f"{method}_data", list):
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
        result = request(**self.__request_builder(method))
        response = self.response_model.convert_raw_response(result)
        if base_validation and not response == self.response_model:
            raise RestResponseValidationError(response)
        return response


def endpoint_factory(base_url: str, class_name: str, request_model: Type[BaseRequestModel],
                     response_model: Type[BaseResponseModel], superclass=BaseEndpoint,
                     make_url_method=make_request_url) -> Union[Callable[[], BaseEndpoint], BaseEndpoint]:
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
    dummy_class = type(class_name, (superclass,), dict(request_model=request_model,
                                                       response_model=response_model,
                                                       base_url=base_url,
                                                       make_url_method=make_url_method))
    return lambda: dummy_class(base_url, request_model(), response_model(), make_url_method)
