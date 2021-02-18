import os

from common._libs.helpers.os_helpers import get_timestamp, create_folder
from common.config_parser.section.base_section import ConfigSection


class BaseGlobalSection:
    """Create base global section if there is no global section in the
    configuration.
    """

    def __init__(self):
        """Basic initialization."""
        self.logdir = 'Logs'
        self.log_level = 'INFO'
        self.enable_libs_logging = False
        self._session_log_dir = None
        self.sections = []

    @property
    def session_log_dir(self):
        if not self._session_log_dir:
            self._session_log_dir = os.path.join(self.logdir, get_timestamp())
        return self._session_log_dir

    def to_dict(self):
        """Convert to dictionary."""
        fields = [field for field in self.__dict__ if not callable(field)]
        return {field: getattr(self, field) for field in fields}


class GlobalSection(ConfigSection, BaseGlobalSection):
    """Class representing a global section of the configuration file.
    """

    SECTION_NAME = 'global'

    def __init__(self, config, custom_args=None):
        self.custom_args = custom_args
        self._settings = []
        BaseGlobalSection.__init__(self)
        ConfigSection.__init__(self, config, self.SECTION_NAME, custom_args=self.custom_args)

    def to_dict(self):
        """Convert to dictionary."""
        return {field: getattr(self, field, None) for field in self._settings}

    def _configure_section(self):
        """
        Divide settings according to their types.
        Set mandatory, comma separated list, space separated list,
        str, bool, int, list of fields if it is necessary.
        """
        self._mandatory_fields = ['logdir', 'sections']
        self._space_separated_list_fields = ['sections']
        self._str_fields = ['logdir', 'log_level']
        self._bool_fields = ['enable_libs_logging']
        self._int_fields = []
        self._settings = self._str_fields + self._bool_fields + self._int_fields + self._space_separated_list_fields

    def _check_settings(self):
        pass

    def _perform_custom_tunings(self):
        """Perform custom tunings for obtained settings."""
        super()._perform_custom_tunings()
