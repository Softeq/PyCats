import inspect
import logging
from copy import copy
from typing import TYPE_CHECKING, Union

from common.config_parser.config_dto import APIValidationDTO
from common._rest_qa_api.rest_checkers import BaseRESTCheckers
from common._rest_qa_api.rest_utils import SKIP

if TYPE_CHECKING:
    # to avoid import loop only for annotations
    from common._rest_qa_api.base_endpoint import BaseResponseModel
    from common._rest_qa_api.response_converter import ResponseConverterMixin

logger = logging.getLogger(__name__)


class ResponseValidatorMixin:
    """
    Mixin to provide a mechanism to compare the response model with the actual response.
    Validation is archived using the __eq__ method override.

    Because self contains the response in BaseResponseModel format we compare it with the provided model.
    During the verification, all errors are saved in self.errors.
    2 types of validations are supported: default validation according to the model and custom user checkers.

    The default validation rules are initialized based on the config values. It is possible to override them for each
    endpoint separately.
    It is also possible to provide additional custom checkers by adding them to the custom_checkers list.
    """

    _check_status_code = None
    _check_headers = None
    _check_body = None
    _check_is_field_missing = None

    def __init__(self, api_validation_section: APIValidationDTO):
        self._check_status_code = self._check_status_code if self._check_status_code is not None \
            else api_validation_section.check_status_code
        self._check_headers = self._check_headers if self._check_headers is not None\
            else api_validation_section.check_headers
        self._check_body = self._check_body if self._check_body is not None\
            else api_validation_section.check_body
        self._check_is_field_missing = self._check_is_field_missing if self._check_is_field_missing is not None\
            else api_validation_section.check_is_field_missing

    @classmethod
    def configure_validator(cls, validate_status_code=True, validate_headers=True, validate_body=True,
                            validate_is_field_missing=True):
        """Performs default validators setup for endpoint if default values should be override.
        Args:
            validate_status_code (bool): Performs status code validation if True
            validate_headers (bool): Performs headers validation if True
            validate_body (bool): Performs body validation if True
            validate_is_field_missing (bool): Fail validation if some field from model is absent in response.
            Added for cases when response may contain only part of model's values and it is expected.
        """
        cls._check_status_code = validate_status_code
        cls._check_headers = validate_headers
        cls._check_body = validate_body
        cls._check_is_field_missing = validate_is_field_missing

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
        if self._check_headers:
            self._validate_structure('headers', self.headers, model.headers)
        if self._check_body:
            self._validate_structure(property_name, body_to_verify, model_data)
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
                        # for case when key is absent in response. If _check_is_field_missing is False
                        # logs warning message
                        if self._check_is_field_missing:
                            self.field_nesting.append(key)
                            self.errors["default"].append((copy(self.field_nesting), model_to_verify[key],
                                                           "field does not present in response"))
                            self.field_nesting.pop()
                        else:
                            logger.warning(f"The field '{key}' is not present in response. Please verify your model")
            elif self._check_is_field_missing:
                self.errors["default"].append((copy(self.field_nesting), model_to_verify, data_to_verify))
            else:
                logger.warning(f"Expected '{model_to_verify}' in response, but got '{data_to_verify}'. "
                               f"Please verify your model")

        elif isinstance(data_to_verify, list):
            # if for cases when model or data is empty list
            if model_to_verify and data_to_verify:
                for number, item in enumerate(model_to_verify):
                    # add element position in list
                    self.field_nesting.append(number)
                    try:
                        self._validate_structure(field_name, data_to_verify[number], model_to_verify[number], number)
                        self.field_nesting.pop()
                    except IndexError:
                        # if there is no element in list
                        self.errors["default"].append((copy(self.field_nesting), model_to_verify, data_to_verify))
            # for cases when expected empty list
            elif not model_to_verify and not data_to_verify:
                pass
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
                if not self.errors["default"] and not self.errors["custom"]:
                    logger.info(f"{checker.__name__} validation passed")
