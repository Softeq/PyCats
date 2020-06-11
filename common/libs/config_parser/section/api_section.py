from common.libs.config_parser.section.base_section import ConfigSection

API_SECTION = "api"


class APISection(ConfigSection):
    """Class responsible for api section parsing."""

    def __init__(self, config, custom_args):
        """Basic initialization."""

        self.api_url = None
        self.config = config
        self.custom_args = custom_args

        super().__init__(config, API_SECTION, custom_args=custom_args)

    def _configure_section(self):
        """Divide settings according to their types.
        Set mandatory,comma separated list, space separated list, str,
        bool, int, list of nodes fields if it is necessary.
        """

        self._mandatory_fields = ['api_url']
        self._str_fields = ['api_url']
        self._int_fields = []
        self._settings = self._str_fields + self._int_fields

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
