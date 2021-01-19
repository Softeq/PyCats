import pytest

from common._webdriver_qa_api.mobile.mobile_driver import MobileDriver
from common.facade import logger, raw_config, config_manager
from common._webdriver_qa_api.web.web_driver import start_webui, stop_webui, navigate_to
from common._webdriver_qa_api.core.remote_server import SeleniumServer, AppiumRemoteServer
from project.test_data.users import valid_user
from project.web.steps.home import HomePageSteps
from project.web.steps.main import MainPageSteps
from project.web.steps.sign_in import SignInSteps


@pytest.fixture(scope="session", autouse=False)
def start_remote_server(request):
    server = SeleniumServer(config_manager)

    def finalizer():
        server.stop_server()
    request.addfinalizer(finalizer)
    server.start_server()


@pytest.fixture(scope="function", autouse=False)
def open_browser(request, start_remote_server):
    logger.log_step("Open Browser", precondition=True)

    def finalizer():
        stop_webui()
    request.addfinalizer(finalizer)
    start_webui(config_manager)


@pytest.fixture(scope="function", autouse=False)
def open_main_page(open_browser):
    logger.log_step("Open Main application page", precondition=True)
    navigate_to(raw_config.project_settings.web_app_url)


@pytest.fixture(scope="module", autouse=False)
def api_token(start_remote_server):
    logger.log_step("Retrieve API token from UI", precondition=True)
    try:
        start_webui(config_manager)
        navigate_to(raw_config.project_settings.web_app_url)
        main_page = MainPageSteps()
        main_page.click_login()

        login_steps = SignInSteps()
        login_steps.login(email=valid_user.email, password=valid_user.password)

        home_steps = HomePageSteps()
        api_key = home_steps.get_api_key()
    finally:
        stop_webui()
    return api_key


@pytest.fixture(scope='session', autouse=False)
def start_mobile_server(request):
    server = AppiumRemoteServer(config_manager)

    def teardown():
        server.stop_server()
    request.addfinalizer(teardown)

    server.start_server()


@pytest.fixture(scope='function', autouse=False)
def start_mobile_session(request, start_mobile_server):
    logger.log_step("Start mobile session", precondition=True)
    # platfrom = config_manager.config.mobile_settings.platform
    # android_config(request.config.getoption("--android_device")) if platfrom == 'android' else \
    #     ios_config(request.config.getoption("--ios_device"))
    mobile_session = MobileDriver(config_manager)

    def test_teardown():
        mobile_session.quit()

    request.addfinalizer(test_teardown)
