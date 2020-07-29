import os
from common.pycats_facade import PyCatsFacade, PyCatsError

pytest_plugins = [
    "common.hooks.cli_options",
    "common.hooks.logger_hooks"
]


def pytest_addhooks(pluginmanager):
    """Setup the framework config and logger firstly"""
    if not pluginmanager.rewrite_hook.config.inicfg:
        raise PyCatsError("Missing or empty 'pytest.ini' file")
    elif not pluginmanager.rewrite_hook.config.inicfg.config.get('pytest', 'config_dir'):
        raise PyCatsError("Missing 'config_dir' option 'pytest' section of 'pytest.ini' file")

    config_dir = pluginmanager.rewrite_hook.config.inicfg.config.get('pytest', 'config_dir')
    config_dir = config_dir if os.path.isabs(config_dir) else \
        os.path.join(pluginmanager.rewrite_hook.config.rootdir, config_dir)

    facade = PyCatsFacade()
    facade.setup_config(config_dir=config_dir)
    facade.setup_logger(None)
