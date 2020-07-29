from common._libs.config_parser.section.base_section import ConfigSection


class ProjectSection(ConfigSection):
    """Class responsible for project section parsing."""

    SECTION_NAME = 'project'

    def __init__(self, config, custom_args):
        """Basic initialization."""
        self.web_app_url = None
        self.web_api_url = None
        self.config = config
        self.custom_args = custom_args
        self._settings = []

        super().__init__(config, self.SECTION_NAME, custom_args=custom_args)

    def _configure_section(self):
        """Divide settings according to their types.
        Set mandatory,comma separated list, space separated list, str,
        bool, int, list of nodes fields if it is necessary.
        """

        self._mandatory_fields = ['web_app_url', 'web_api_url']
        self._str_fields = ['web_app_url', 'web_api_url']
        self._settings = self._str_fields

    def _perform_custom_tunings(self):
        """Perform custom tunings for obtained settings."""
        for setting in self._settings:
            if setting in self._untuned_settings:
                setattr(self, setting, self._untuned_settings[setting])

        if self.custom_args is not None:
            self._tune_custom_args()

    def _check_settings(self):
        pass
