"""
This module contains the ParseConfig class, used to parse the
frameworks configuration file.
"""

import os
from collections import Counter
from typing import Optional

from configparser import ConfigParser

from common._libs.config_parser.section.api_section import APISection
from common._libs.config_parser.section.base_section import ConfigSection
from common._libs.config_parser.config_error import ConfigError
from common._libs.config_parser.section.global_section import GlobalSection, BaseGlobalSection
from common._libs.config_parser.section.web_section import WebSection


class ParseConfig:
    """Class responsible for parsing the frameworks configuration
     file, and managing the parsed database. It uses the ConfigParser
     module to handle that.

     Attributes:
         config_file:             An absolute path to the config.
         config:                  ConfigParser object.
         global_settings:         GlobalSection/BaseGlobalSection object.
         api_settings:            

    Examples:
      config = ParseConfig('config/test.conf')

      Access global settings:
        logdir = config.global_settings.logdir
        log_level = config.global_settings.log_level
        enable_libs_logging = config.global_settings.enable_libs_logging
    """

    def __init__(self, config_file, custom_args=None):
        """Create a parser object. Verify if specified sections
        (global, node, build) exist.

        Args:
            config_file (str):  An absolute path to the configuration file.
        """
        if not os.path.exists(config_file):
            raise ConfigError(f"Unable to found configuration file '{config_file}'")
        self.custom_args = custom_args
        self.config_file = config_file
        self.config = ConfigParser()
        self.config.read(config_file)

        self.global_settings: Optional[GlobalSection] = None
        self.sections = None
        self.api_settings: Optional[APISection] = None
        self.web_settings: Optional[WebSection] = None

        self._verify_duplicated_options()

        self._tune_global()

        if self.global_settings.sections:
            self._tune_sections()

    def _tune_global(self):
        """Tune global settings. If there is no 'global' section
        in the configuration file, the FakeGlobalSection global
        section will be created with the default parameters for
        'logdir' and 'enable_libs_logging'.
        """
        if self.config.has_section('global'):
            self.global_settings = GlobalSection(self.config, self.custom_args)
        else:
            self.global_settings = BaseGlobalSection()

    def _tune_sections(self):
        sections_mapping = {"api": APISection,
                            "web": WebSection}
        for section in self.global_settings.sections:
            ConfigSection.check_if_section_exists(self.config, section, None)
            setattr(self, f"{section}_settings", sections_mapping[section](self.config, self.custom_args))

    def _verify_duplicated_options(self):
        sections = self.config.sections()
        options = []
        for section in sections:
            options.extend([option[0] for option in self.config.items(section)])
        duplicated_options = [k for k, v in Counter(options).items() if v > 1]
        if duplicated_options:
            raise ConfigError(f"The following option(s) in config are duplicated. "
                              f"Please use another name: {duplicated_options}")
