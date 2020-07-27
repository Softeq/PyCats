"""
This module provides interfaces to access internal framework components like config, logger, libraries, api.
All communication with internal PyCats modules should be done via this module.
Also it provides shortcuts for the long function or data names
"""

from common.pycats_facade import PyCatsFacade

pycats = PyCatsFacade()
config_manager = pycats.config_manager
raw_config = pycats.config_manager.config
logger = pycats.logger
