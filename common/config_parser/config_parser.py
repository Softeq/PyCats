"""
This module contains the ParseConfig class, used to parse the
frameworks configuration file.
"""
import importlib
import inspect
import os
from collections import Counter
from typing import Optional

from configparser import ConfigParser

from common.config_parser.section.api_validation_section import APIValidationSection
from common.config_parser.section.base_section import ConfigSection
from common.config_parser.config_error import ConfigError
from common.config_parser.section.global_section import GlobalSection, BaseGlobalSection
from common.config_parser.section.web_section import WebSection
from common._libs.helpers.utils import get_modules_list


class ParseConfig:
    """Class responsible for parsing the frameworks configuration
     file, and managing the parsed database. It uses the ConfigParser
     module to handle that.

     Attributes:
         config_dir:              An absolute path to the configs directory.
         config:                  ConfigParser object.
         global_settings:         GlobalSection/BaseGlobalSection object.
         api_validation_settings: APIValidationSection object
         web_settings:            WebSection object

    Examples:
      config = ParseConfig('/home/user/config')

      Access global settings:
        logdir = config.global_settings.logdir
        log_level = config.global_settings.log_level
        enable_libs_logging = config.global_settings.enable_libs_logging
    """

    def __init__(self, config_dir, custom_args=None):
        """Create a parser object. Verify if PyCats configuration files present in specified folder.
        Verify if required sections and options are exist in config files

        Args:
            config_dir (str):  An absolute path to the configs directory.
        """
        if not os.path.exists(config_dir):
            raise ConfigError(f"Unable to find configuration folder '{config_dir}'")

        self.config_files = [os.path.join(config_dir, f) for f in os.listdir(config_dir)
                             if f.lower().startswith('pycats') and f.lower().endswith('.ini')]
        if not config_dir:
            raise ConfigError(f"Unable to find PyCats configuration files in '{config_dir}' folder")

        self.custom_args = custom_args
        self.config_dir = config_dir
        self.config = ConfigParser()
        self.config.read(self.config_files)

        self.global_settings: Optional[GlobalSection] = None
        self.api_validation_settings: Optional[APIValidationSection] = None
        self.web_settings: Optional[WebSection] = None

        self._verify_duplicated_options()

        self._tune_global()
        self._tune_api_validations_section()
        self._tune_web_section()
        self._tune_project_sections()

    def _tune_global(self):
        """Tune global settings. If there is no 'global' section
        in the configuration file, the FakeGlobalSection global
        section will be created with the default parameters for
        'logdir' and 'enable_libs_logging'.
        """
        if self.config.has_section(GlobalSection.SECTION_NAME):
            self.global_settings = GlobalSection(self.config, self.custom_args)
        else:
            self.global_settings = BaseGlobalSection()

    def _tune_api_validations_section(self):
        setattr(self, f"{APIValidationSection.SECTION_NAME}_settings",
                APIValidationSection(self.config, self.custom_args))

    def _tune_web_section(self):
        setattr(self, f"{WebSection.SECTION_NAME}_settings",
                WebSection(self.config, self.custom_args))

    def _tune_project_sections(self):
        # import sections modules from config directory
        modules_list = get_modules_list(self.config_dir, "**/")
        for name in modules_list:
            module = importlib.import_module(name)
            # filter all classes in imported module to find childes of ConfigSection
            sections = [value for key, value in inspect.getmembers(module, inspect.isclass)
                        if value.__base__ == ConfigSection]
            if sections:
                for section in sections:
                    setattr(self, f"{section.SECTION_NAME}_settings", section(self.config, self.custom_args))

    def _verify_duplicated_options(self):
        sections = self.config.sections()
        options = []
        for section in sections:
            options.extend([option[0] for option in self.config.items(section)])
        duplicated_options = [k for k, v in Counter(options).items() if v > 1]
        if duplicated_options:
            raise ConfigError(f"The following option(s) in config are duplicated. "
                              f"Please use another name: {duplicated_options}")
