from common.config_parser.config_dto import APIValidationDTO, WebDriverSettingsDTO
from common.config_parser.config_parser import ParseConfig
from common._libs.helpers.singleton import Singleton


class ConfigManager(metaclass=Singleton):

    def __init__(self, config_dir=None):
        self.config_dir = config_dir
        self.config = ParseConfig(self.config_dir)
        self.cli_update = None

    def get_config(self):
        return self.config

    def update_config(self, custom_args):
        self.config = ParseConfig(self.config_dir, custom_args)

    def get_api_validations(self) -> APIValidationDTO:
        settings = self.config.api_validation_settings
        return APIValidationDTO(settings.validate_status_code, settings.validate_headers,
                                settings.validate_body, settings.validate_is_field_missing)

    def get_webdriver_settings(self) -> WebDriverSettingsDTO:
        settings = self.config.web_settings
        return WebDriverSettingsDTO(settings.webdriver_folder, settings.webdriver_default_wait_time,
                                    settings.webdriver_implicit_wait_time, settings.selenium_server_executable,
                                    settings.chrome_driver_name, settings.firefox_driver_name, settings.browser,
                                    settings.driver_path, settings.chrome_options)
