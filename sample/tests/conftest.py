import pytest

from common._webdriver_qa_api.mobile.mobile_driver import MobileDriver
from common._webdriver_qa_api.core.screenshot_manager import WebScreenShot, MobileScreenShot
from common.facade import logger, raw_config, config_manager
from common._webdriver_qa_api.web.web_driver import start_webdriver_session, stop_webdriver_session, navigate_to
from common._webdriver_qa_api.core.remote_server import SeleniumServer, AppiumRemoteServer
from sample.test_data.users import valid_user
from sample.web.steps.page_object_steps.pages.home import HomePageSteps
from sample.web.steps.page_object_steps.pages.main import MainPageSteps
from sample.web.steps.page_object_steps.pages.sign_in import SignInSteps


@pytest.fixture(scope="session", autouse=False)
def start_remote_server(request):
    server = SeleniumServer(config_manager.get_webdriver_settings())

    def finalizer():
        server.stop_server()
    request.addfinalizer(finalizer)
    server.start_server()


@pytest.fixture(scope="function", autouse=False)
def open_browser(request, start_remote_server):
    logger.log_step("Open Browser", precondition=True)

    def finalizer():
        WebScreenShot(screen_path=logger.log_dir).save_screenshot(request.node.name)
        stop_webdriver_session()
    request.addfinalizer(finalizer)
    start_webdriver_session(config_manager.get_webdriver_settings())


@pytest.fixture(scope="function", autouse=False)
def open_main_page(open_browser):
    logger.log_step("Open Main application page", precondition=True)
    navigate_to(raw_config.project_settings.web_app_url)


@pytest.fixture(scope="module", autouse=False)
def api_token(start_remote_server):
    logger.log_step("Retrieve API token from UI", precondition=True)
    try:
        start_webdriver_session(config_manager.get_webdriver_settings())
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


@pytest.fixture(scope='session', autouse=False)
def start_mobile_server(request):
    server = AppiumRemoteServer(config_manager.get_mobile_settings())

    def teardown():
        server.stop_server()
    request.addfinalizer(teardown)

    server.start_server()


@pytest.fixture(scope='function', autouse=False)
def start_mobile_session(request, start_mobile_server):
    logger.log_step("Start mobile session", precondition=True)
    mobile_session = MobileDriver(config_manager.get_mobile_settings())

    def test_teardown():
        MobileScreenShot(screen_path=logger.log_dir).save_screenshot(request.node.name)
        mobile_session.quit()

    request.addfinalizer(test_teardown)
