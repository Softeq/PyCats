from common.scaf_facade import SCAFFacade

pytest_plugins = [
    "common.hooks.cli_options",
    "common.hooks.logger_hooks"
]


def pytest_addhooks(pluginmanager):
    """Setup the framework config and logger firstly"""
    facade = SCAFFacade()
    facade.setup_config(None)
    facade.setup_logger(None)
    facade.rebind_submodules_logger(exclude_packages=["common.scaf"])
