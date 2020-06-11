from common.scaf_facade import SCAFFacade

from _pytest.config.argparsing import Parser

API_URL = '--api_url'

APP_URL = '--app_url'
BROWSER = '--browser'
DRIVER_PATH = '--driver_path'
WEBDRIVER_FOLDER = '--webdriver_folder'

CLI_ARGS = [BROWSER, WEBDRIVER_FOLDER]


def pytest_addoption(parser: Parser):
    api_group = parser.getgroup("api", after="web")
    api_group.addoption(API_URL,
                        help='Base URL of the application API')

    web_group = parser.getgroup("web")
    web_group.addoption(APP_URL,
                        help='Base URL of the application')
    web_group.addoption(BROWSER,
                        help='Possible values: '
                             'chrome | firefox')
    web_group.addoption(WEBDRIVER_FOLDER,
                        help='Path to folder with browser driver')


def get_cli_args(config, args):
    cli_args = {}
    for arg in args:
        arg_name = arg.strip('--')
        cli_args[arg_name] = config.getoption(arg)
    return cli_args


def pytest_configure(config):
    """Update config with value from CLI arguments"""
    args = get_cli_args(config, CLI_ARGS)
    SCAFFacade().config_manager.update_config(custom_args=args)
