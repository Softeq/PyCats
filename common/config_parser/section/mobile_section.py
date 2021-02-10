import os

from common.config_parser.section.base_section import ConfigSection
from common.config_parser.config_error import ConfigError

ALLOWED_PLATFORMS_LIST = ["android", "ios"]


class MobileSection(ConfigSection):
    """Class responsible for mobile section parsing."""

    SECTION_NAME = 'mobile'

    def __init__(self, config, custom_args):
        """Basic initialization."""

        self.appium_server_path = None
        self.node_executable_path = None
        self.default_wait_time = 20
        self.implicit_wait_time = 30

        self.platform = None
        self.ios_udid = None
        self.ipa_path = None

        self.android_udid = None
        self.android_package = None
        self.android_activity = None

        self.config = config
        self.custom_args = custom_args
        self._settings = []

        super().__init__(config, self.SECTION_NAME, custom_args=custom_args)

    def _configure_section(self):
        """Divide settings according to their types.
        Set mandatory,comma separated list, space separated list, str,
        bool, int, list of nodes fields if it is necessary.
        """
        # todo: check _mandatory_fields based on parameter from config?
        self._mandatory_fields = ['appium_server_path', 'node_executable_path']
        self._str_fields = ['appium_server_path', 'node_executable_path', 'platform',
                            'ios_udid', 'ipa_path', 'android_udid', 'android_package', 'android_activity']
        self._int_fields = ['default_wait_time', 'implicit_wait_time']
        self._settings = self._str_fields

    def to_dict(self):
        """Convert to dictionary."""
        return {field: getattr(self, field, None) for field in self._settings}

    def _load_from_config(self):
        super()._load_from_config()

    def _perform_custom_tunings(self):
        """Perform custom tunings for obtained settings."""
        for setting in self._settings:
            if setting in self._untuned_settings:
                setattr(self, setting, self._untuned_settings[setting])

        if self.custom_args is not None:
            self._tune_custom_args()

    def _check_settings(self):
        """Check if settings are valid."""
        if not os.path.exists(self.appium_server_path):
            raise ConfigError(f"Unable to find appium server executable file in provided path: "
                              f"{self.appium_server_path}")

        if self.platform not in ALLOWED_PLATFORMS_LIST:
            raise ConfigError(f"Unexpected mobile platform provided {self.platform}, "
                              f"possible types: {ALLOWED_PLATFORMS_LIST}")
