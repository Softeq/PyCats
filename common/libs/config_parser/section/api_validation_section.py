from configparser import ConfigParser

from common.libs.config_parser.config_error import ConfigError
from common.libs.config_parser.section.base_section import ConfigSection


class APIValidationSection(ConfigSection):
    """Class responsible for api validation rules section parsing."""

    SECTION_NAME = 'api_validation'

    def __init__(self, config, custom_args):
        """Basic initialization."""
        self.validate_status_code = True
        self.validate_headers = True
        self.validate_body = True
        self.validate_is_field_missing = True
        self.config: ConfigParser = config
        self.custom_args = custom_args
        self._settings = []

        super().__init__(config, self.SECTION_NAME, custom_args=custom_args)

    def _configure_section(self):
        """Divide settings according to their types.
        Set mandatory,comma separated list, space separated list, str,
        bool, int, list of nodes fields if it is necessary.
        """
        self._mandatory_fields = []
        self._str_fields = []
        self._int_fields = []
        self._bool_fields = ['validate_status_code', 'validate_headers', 'validate_body',
                             'validate_is_field_missing']
        self._settings = self._str_fields + self._int_fields + self._bool_fields

    def _load_from_config(self):
        """Add a section to initial config object if it absences to support optional logic for section and
        execute default _load_from_config behaviour"""
        try:
            self.check_if_section_exists(self.config, self.SECTION_NAME, None)
        except ConfigError:
            self.config.add_section(self.SECTION_NAME)
        super()._load_from_config()

    def to_dict(self):
        """Convert to dictionary."""
        return {field: getattr(self, field, None) for field in self._settings}

    def _perform_custom_tunings(self):
        """Perform custom tunings for obtained settings."""
        for setting in self._settings:
            if setting in self._untuned_settings:
                setattr(self, setting, self._untuned_settings[setting])

        if self.custom_args is not None:
            self._tune_custom_args()

    def _check_settings(self):
        pass
