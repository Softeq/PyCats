import pytest

from common.facade import logger, raw_config, config_manager
from common._webdriver_qa_api.web.web_driver import start_webdriver_session, stop_webdriver_session, navigate_to
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


@pytest.fixture(scope="function", autouse=False)
def open_browser(request):
    logger.log_step("Open Browser", precondition=True)

    def finalizer():
        stop_webdriver_session()
    request.addfinalizer(finalizer)
    start_webdriver_session(config_manager)


@pytest.fixture(scope="function", autouse=False)
def open_main_page(open_browser):
    logger.log_step("Open Main application page", precondition=True)
    navigate_to(raw_config.project_settings.web_app_url)


@pytest.fixture(scope="module", autouse=False)
def api_token():
    logger.log_step("Retrieve API token from UI", precondition=True)
    try:
        start_webdriver_session(config_manager)
        navigate_to(raw_config.project_settings.web_app_url)
        main_page = MainPageSteps()
        main_page.click_sign_in()

        login_steps = SignInSteps()
        login_steps.login(email=valid_user.email, password=valid_user.password)

        home_steps = HomePageSteps()
        api_key = home_steps.get_api_key()
    finally:
        stop_webdriver_session()
    return api_key
