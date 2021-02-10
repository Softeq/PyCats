import os

from common.config_parser.section.base_section import ConfigSection
from common.config_parser.config_error import ConfigError

WEB_SECTION = "web"

BROWSER_SETTINGS_MAPPING = {"chrome": "chrome_driver_name",
                            "firefox": "firefox_driver_name"}

ALLOWED_BROWSER_LIST = ["chrome", "firefox"]


class WebSection(ConfigSection):
    """Class responsible for ui section parsing."""

    SECTION_NAME = 'web'

    def __init__(self, config, custom_args):
        """Basic initialization."""
        self.webdriver_folder = None
        self.default_wait_time = 20
        self.implicit_wait_time = 30
        self.selenium_server_executable = None
        self.chrome_driver_name = None
        self.firefox_driver_name = None
        self.browser = 'chrome'
        self.driver_path = None
        self.config = config
        self.custom_args = custom_args
        self._settings = []

        super().__init__(config, self.SECTION_NAME, custom_args=custom_args)

    def _configure_section(self):
        """Divide settings according to their types.
        Set mandatory,comma separated list, space separated list, str,
        bool, int, list of nodes fields if it is necessary.
        """

        self._mandatory_fields = ['webdriver_folder', 'chrome_driver_name']
        self._str_fields = ['webdriver_folder', 'selenium_server_executable', 'chrome_driver_name',
                            'firefox_driver_name', 'browser']
        self._int_fields = ['default_wait_time', 'implicit_wait_time']
        self._settings = self._str_fields + self._int_fields

    def to_dict(self):
        """Convert to dictionary."""
        return {field: getattr(self, field, None) for field in self._settings}

    def _load_from_config(self):
        super()._load_from_config()

    def _perform_custom_tunings(self):
        """Perform custom tunings for obtained settings."""
        super()._perform_custom_tunings()

    def _check_settings(self):
        """Check if webdriver settings are valid."""
        self.driver_path = self.get_driver_path()
        if self.browser not in ALLOWED_BROWSER_LIST:
            raise ConfigError(f"Unexpected browser provided {self.browser}, "
                              f"possible types: {ALLOWED_BROWSER_LIST}")
        if not os.path.exists(self.selenium_server_executable):
            raise ConfigError(f"Unable to find selenium server executable file in provided path: "
                              f"{self.selenium_server_executable}")

        if not os.path.exists(self.driver_path):
            raise ConfigError(f"Unable to find {self.browser} driver file in provided path: "
                              f"{self.driver_path}")

    def get_driver_path(self):
        driver_variable = BROWSER_SETTINGS_MAPPING[self.browser]
        driver_path = os.path.join(self.webdriver_folder, getattr(self, driver_variable))
        return driver_path
