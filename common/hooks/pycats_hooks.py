from common.pycats_facade import PyCatsFacade

pytest_plugins = [
    "common.hooks.cli_options",
    "common.hooks.logger_hooks"
]


def pytest_addhooks(pluginmanager):
    """Setup the framework config and logger firstly"""
    if not pluginmanager.rewrite_hook.config.inicfg:
        raise Exception("Missing or empty 'pytest.ini' file")
    elif not pluginmanager.rewrite_hook.config.inicfg.config.get('pytest', 'config_dir'):
        raise Exception("Missing 'config_dir' option 'pytest' section of 'pytest.ini' file")

    facade = PyCatsFacade()
    facade.setup_config(config_dir=pluginmanager.rewrite_hook.config.inicfg.config.get('pytest', 'config_dir'))
    facade.setup_logger(None)
