from abc import ABCMeta, abstractmethod

from common._libs.config_parser.config_error import ConfigError


class ConfigSection(metaclass=ABCMeta):
    """An abstract base class representing a base section of the
    configuration file. Any specific section class must derive from it.
    """

    def __init__(self, config, section_name, shadow_config=None, custom_args=None):
        """Basic initialization."""

        self._config = config
        self._section_name = section_name
        self._shadow_config = shadow_config
        self._custom_args = custom_args

        self._mandatory_fields = list()
        self._comma_separated_list_fields = list()
        self._space_separated_list_fields = list()
        self._str_fields = list()
        self._bool_fields = list()
        self._int_fields = list()

        self._untuned_settings = dict()
        self.unknown_settings = dict()

        self._configure_section()
        self._load_from_config()

    @abstractmethod
    def _configure_section(self):
        """Divide settings according to their types.
        Set mandatory, comma separated list, space separated list,
        str, bool, int, list of nodes fields if it is necessary.
        """
        pass

    def _load_from_config(self):
        """Load section from configuration file."""

        self._load_settings_from_config()

        self._load_unknown_settings_from_config()

        self._perform_custom_tunings()

        self._check_mandatory_fields_present()

        self._check_settings()

    def _load_settings_from_config(self):
        """Load settings from the configuration file."""

        for int_setting in self._int_fields:
            if self._config.has_option(self._section_name, int_setting):
                self._untuned_settings[int_setting] = self._config.getint(
                    self._section_name, int_setting)
            if self._shadow_config is not None:
                if self._shadow_config.has_option(
                        self._section_name, int_setting):
                    self._untuned_settings[
                        int_setting] = self._shadow_config.getint(
                        self._section_name, int_setting)

        for bool_setting in self._bool_fields:
            if self._config.has_option(self._section_name, bool_setting):
                self._untuned_settings[
                    bool_setting] = self._config.getboolean(
                    self._section_name, bool_setting)
            if self._shadow_config is not None:
                if self._shadow_config.has_option(
                        self._section_name, bool_setting):
                    self._untuned_settings[
                        bool_setting] = self._shadow_config.getboolean(
                        self._section_name, bool_setting)

        for str_setting in self._str_fields:
            if self._config.has_option(self._section_name, str_setting):
                self._untuned_settings[str_setting] = self._config.get(
                    self._section_name, str_setting)
            if self._shadow_config is not None:
                if self._shadow_config.has_option(
                        self._section_name, str_setting):
                    self._untuned_settings[
                        str_setting] = self._shadow_config.get(
                        self._section_name, str_setting)

        for comma_separated_list_setting in self._comma_separated_list_fields:
            if self._config.has_option(
                    self._section_name, comma_separated_list_setting):
                self._untuned_settings[
                    comma_separated_list_setting] = self.__split_list_settings(
                    self._config.get(
                        self._section_name, comma_separated_list_setting), ',')
            if self._shadow_config is not None:
                if self._shadow_config.has_option(
                        self._section_name, comma_separated_list_setting):
                    self._untuned_settings[
                        comma_separated_list_setting] = self.__split_list_settings(
                        self._shadow_config.get(
                            self._section_name,
                            comma_separated_list_setting), ',')

        for space_separated_list_setting in self._space_separated_list_fields:
            if self._config.has_option(
                    self._section_name, space_separated_list_setting):
                self._untuned_settings[
                    space_separated_list_setting] = self.__split_list_settings(
                    self._config.get(
                        self._section_name, space_separated_list_setting), ' ')
            if self._shadow_config is not None:
                if self._shadow_config.has_option(
                        self._section_name, space_separated_list_setting):
                    self._untuned_settings[
                        space_separated_list_setting] = self.__split_list_settings(
                        self._shadow_config.get(
                            self._section_name,
                            space_separated_list_setting), ' ')

    def _load_unknown_settings_from_config(self):
        """Load unknown settings from the configuration file."""

        known_settings = \
            self._int_fields + self._str_fields + \
            self._bool_fields + self._comma_separated_list_fields + \
            self._space_separated_list_fields

        self.unknown_settings = {
            setting: self._config.get(self._section_name, setting)
            for setting in self._config.options(self._section_name)
            if setting not in known_settings}

        if self._shadow_config is not None:
            if self._shadow_config.has_section(self._section_name):
                self.unknown_settings.update(
                    {setting: self._shadow_config.get(
                        self._section_name, setting)
                        for setting in self._shadow_config.options(
                        self._section_name) if setting not in known_settings})

    @abstractmethod
    def _perform_custom_tunings(self):
        """Perform custom tunings for obtained settings."""
        pass

    def _tune_custom_args(self):
        if not isinstance(self._custom_args, dict):
            raise ConfigError("Custom CLI arguments are not in a "
                              "dictionary.")
        for key, value in self._custom_args.items():
            if value is not None and key in self.__dict__:
                setattr(self, key, value)

    def _check_mandatory_fields_present(self):
        """Check if all mandatory fields are present in
        the configuration section after all tunings."""
        self.verify_fields_presence(self._mandatory_fields)

    @abstractmethod
    def _check_settings(self):
        """Check if obtained settings meet all necessary conditions.
        """
        pass

    def verify_fields_presence(self, fields, message=None):
        """Check if all provided fields are present in
        the configuration section.

        Args:
            fields (list): A list of attributes to check.
            message (str):  Message to display in case of an error.
        """
        for field in fields:
            if getattr(self, field) in [None, '']:
                error_msg = f"In section '{self._section_name}' of the configuration " \
                            f"file setting '{field}' is required {'.' if not message else f' For {message}'}"
                raise ConfigError(error_msg)

    @staticmethod
    def check_if_section_exists(config, section_template, section):
        """Check if section exists.
        Examples:
          Check if section exists:
            api_section = 'api_{}'
            ConfigSection.check_if_section_exists(config_obj,
                                                  node_section,
                                                  None)
        """
        if not config.has_section(section_template.format(section)):
            raise ConfigError(f"No section '{section_template.format(section)}' "
                              f"found in the configuration file.")

    @staticmethod
    def __split_list_settings(value, separator):
        """Split value by given separator."""

        stripped = (a.strip() for a in value.split(separator))
        return list(a for a in stripped if len(a))
