import pytest

from common.facade import logger, raw_config, config_manager
from common._webdriver_qa_api.web.web_driver import start_webui, stop_webui, navigate_to
from common._webdriver_qa_api.web.remote_server import SeleniumServer
from project.test_data.users import valid_user
from project.web.steps.home import HomePageSteps
from project.web.steps.main import MainPageSteps
from project.web.steps.sign_in import SignInSteps


@pytest.fixture(scope="session", autouse=True)
def start_remote_server(request):
    server = SeleniumServer(config_manager)

    def finalizer():
        server.stop_server()
    request.addfinalizer(finalizer)
    server.start_server()

@pytest.fixture(scope="function", autouse=True)
def open_browser(request):
    logger.log_step("Open Browser", precondition=True)

    def finalizer():
        stop_webui()
    request.addfinalizer(finalizer)
    start_webui(config_manager)


@pytest.fixture(scope="function", autouse=False)
def main_page():
    logger.log_step("Open Main application page", precondition=True)
    navigate_to(raw_config.web_settings.app_url)


@pytest.fixture(scope="module", autouse=True)
def api_token():
    logger.log_step("Retrieve API token from UI", precondition=True)
    try:
        start_webui(config_manager)
        navigate_to(raw_config.web_settings.app_url)
        main_page = MainPageSteps()
        main_page.click_login()

        login_steps = SignInSteps()
        login_steps.login(valid_user)

        home_steps = HomePageSteps()
        api_key = home_steps.get_api_key()
    finally:
        stop_webui()
    return api_key
