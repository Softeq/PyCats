import os

from common.libs.config_parser.config_dto import APIValidationDTO
from common.libs.config_parser.config_parser import ParseConfig
from common.libs.helpers.singleton import Singleton


class ConfigManager(metaclass=Singleton):
    DEFAULT_CONFIG_PATH = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/config.ini')}"

    def __init__(self, path_to_config=None):
        self.path_to_config = path_to_config or self.DEFAULT_CONFIG_PATH
        self.config = ParseConfig(self.path_to_config)
        self.cli_update = None

    def get_config(self):
        return self.config

    def update_config(self, custom_args):
        self.config = ParseConfig(self.path_to_config, custom_args)

    def get_api_validations(self) -> APIValidationDTO:
        settings = self.config.api_settings.api_validation_settings
        return APIValidationDTO(settings.validate_status_code, settings.validate_headers,
                                settings.validate_body, settings.fail_if_field_is_missing)
