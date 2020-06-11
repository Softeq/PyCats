import logging
from typing import Union, Optional, Any
from common.libs.config_manager import ConfigManager
from common.libs.helpers.singleton import Singleton
from common.libs.logger import SCAFLogger


class FacadeError(Exception):
    pass


class SCAFFacade(metaclass=Singleton):

    def __init__(self):
        self._config_manager: Optional[ConfigManager] = None
        self._logger: Optional[SCAFLogger] = None

    @property
    def config_manager(self) -> ConfigManager:
        if not self._config_manager:
            raise FacadeError("Config was not initialized yet. Please initialize it firstly")
        return self._config_manager

    @config_manager.setter
    def config_manager(self, config):
        if self._config_manager:
            raise FacadeError("Config was already initialized. Facade update is forbidden")
        self.setup_config(config)

    @property
    def logger(self):
        if not self._logger:
            raise FacadeError("Logger was not initialized yet. Please initialize it firstly")
        return self._logger

    @logger.setter
    def logger(self, logger):
        if self._logger:
            raise FacadeError("Logger was already initialized. Facade update is forbidden")
        self.setup_logger(logger)

    def setup_config(self, config: Union[Any, ConfigManager]):
        self._config_manager = config or ConfigManager()

    def setup_logger(self, logger_instance):
        if not self._config_manager:
            raise FacadeError("Logger can not be setup before config. Please setup config before")
        if logger_instance:
            self._logger = logger_instance
        else:
            SCAFLogger.base_log_dir = self.config_manager.config.global_settings.logdir
            SCAFLogger.log_level = self.config_manager.config.global_settings.log_level
            SCAFLogger.enable_libs_logging = self.config_manager.config.global_settings.enable_libs_logging
            self._logger = SCAFLogger(logging.getLogger(__name__))
