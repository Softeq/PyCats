from common.pycats_facade import PyCatsFacade

pytest_plugins = [
    "common.hooks.cli_options",
    "common.hooks.logger_hooks"
]


def pytest_addhooks(pluginmanager):
    """Setup the framework config and logger firstly"""
    facade = PyCatsFacade()
    facade.setup_config(None)
    facade.setup_logger(None)
