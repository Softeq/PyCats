from common.config_parser.config_parser import ConfigSection


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
        super()._perform_custom_tunings()

    def _check_settings(self):
        pass
