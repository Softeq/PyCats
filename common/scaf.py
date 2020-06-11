"""
This module provides interfaces to access internal framework logic like config and logger.
All communication with internal SCAF modules should be done via this module.
Also it provides shortcuts for the long function or data names
"""

import logging
from common.scaf_facade import SCAFFacade
from common.libs.logger import SCAFLogger

scaf = SCAFFacade()
config = scaf.config_manager.config
logger = scaf.logger


def get_logger(logger_name):
    new_logger = SCAFLogger(logging.getLogger(logger_name))
    return new_logger
