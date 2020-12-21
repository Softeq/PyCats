from __future__ import annotations

import logging
from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # to avoid import loop only for annotations
    from common._rest_qa_api.base_endpoint import BaseResponseModel

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class BaseRESTCheckers:
    """Base class to organize checkers in one class and call them automatically during response validation.

    By default, all checkers in class are running. To deactivate checker you can call deactivate() method
    and provide a checker to ignore.

    execute() is called automatically and in case of assertion errors, appends error to the common errors list.
    """
    _deactivated_checks = []

    @classmethod
    def activate(cls, method):
        """Call to activate deactivated checker

        Args:
            method: checker name
        """
        if method in cls._deactivated_checks:
            cls._deactivated_checks.remove(method.__name__)

    @classmethod
    def deactivate(cls, method):
        """Call to deactivate checker

        Args:
            method: checker name
        """
        if method not in cls._deactivated_checks:
            cls._deactivated_checks.append(method.__name__)

    @classmethod
    def execute(cls, response):
        errors = []
        for method in dir(cls):
            if not method.startswith("_") and callable(getattr(cls, method)) and \
                    method not in cls._deactivated_checks\
                    and method not in ["activate", "deactivate", "execute"]:
                try:
                    getattr(cls, method)(response)
                except AssertionError as err:
                    errors.append((method, err))
                else:
                    logger.info(f"{method} validation passed")
        return errors


class JSONCheckers(BaseRESTCheckers):
    status = None
    expected_json_structure = None

    @classmethod
    def check_json_structure(cls, response: BaseResponseModel):
        expected_keys = list(cls.expected_json_structure.keys())
        expected_keys.sort()
        json_keys = list(response.raw_response.json().keys())
        json_keys.sort()
        assert json_keys == expected_keys, "Invalid JSON Structure"

    @classmethod
    def check_status(cls, response: BaseResponseModel):
        logger.info(f"check that status code is {cls.status}")
        assert response.raw_response.status_code == cls.status, \
            f"Invalid status code. Expected '{cls.status}', but got '{response.raw_response.status_code}'"


def check_json_structure(expected_json_structure):
    @wraps(check_json_structure)
    def internal_check_json_structure(response: BaseResponseModel):
        expected_keys = list(expected_json_structure.keys())
        expected_keys.sort()
        json_keys = list(response.raw_response.json().keys())
        json_keys.sort()
        assert json_keys == expected_keys, "Invalid JSON Structure"
    return internal_check_json_structure


def check_status(status: int):
    @wraps(check_status)
    def internal_check_status(response: BaseResponseModel):
        logger.info(f"check that status code is {status}")
        assert response.raw_response.status_code == status, \
            f"Invalid status code. Expected '{status}', but got '{response.raw_response.status_code}'"
    return internal_check_status
