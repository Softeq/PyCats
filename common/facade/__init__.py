"""
This module provides interfaces to access internal framework components like config, logger, libraries, api.
All communication with internal SCAF modules should be done via this module.
Also it provides shortcuts for the long function or data names
"""

from common.scaf_facade import SCAFFacade

scaf = SCAFFacade()
config_manager = scaf.config_manager
raw_config = scaf.config_manager.config
logger = scaf.logger
