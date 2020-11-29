import pytest

from common._webdriver_qa_api.mobile.mobile_driver import MobileDriver
from common.facade import logger, raw_config, config_manager
from common._webdriver_qa_api.web.web_driver import start_webui, stop_webui, navigate_to
from common._webdriver_qa_api.web.remote_server import SeleniumServer, AppiumRemoteServer
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
def main_page():
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
        login_steps.login(valid_user)

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
    MobileDriver(config_manager)

    def test_teardown():
        MobileDriver(config_manager).quit()

    request.addfinalizer(test_teardown)


# def android_config(udid):
#     if udid == 'config':
#         udid = parse_config(section='android_device', option='udid', config_file='mobile.cfg')
#     if udid == 'env_variable':
#         udid = os.environ.get('android_device')
#
#     if udid is not None:
#         os.environ['android_device'] = udid
#     else:
#         raise ValueError("The android_device variable is not set in mobile.cfg or environment variable")
#
#     log("Setup android config for device - {}".format(udid))
#     app_version = Resources().mobile.app_version
#     package = parse_config(section=app_version, option='android_package', config_file='mobile.cfg')
#     activity = parse_config(section=app_version, option='android_activity', config_file='mobile.cfg')
#
#     ANDROID_APP.update(appPackage=package, appActivity=activity, deviceName=udid, udid=udid)
#     DR_MOBILE.update(command_executor=COMMAND_EXECUTOR)
#
#
# def ios_config(udid):
#     app_version = Resources().mobile.app_version
#
#     if udid == 'config':
#         udid = parse_config(section='ios_device', option='udid', config_file='mobile.cfg')
#     if udid == 'env_variable':
#         if os.environ.get('ios_device'):
#             udid = os.environ.get('ios_device')
#         else:
#             raise ValueError("The ios_device variable is not set in mobile.cfg or environment variable")
#
#     ipa_path = parse_config(section=app_version, option='ipa_path', config_file='mobile.cfg')
#     ipa_path = IPA_PATH if ipa_path == 'default' else ipa_path
#
#     log("Setup ios config for device - {}".format(udid))
#     ios_device = get_device_config_by_udid(udid)
#     if ios_device:
#         IOS_APP.update(ios_device, app=ipa_path)
#     else:
#         # todo: think about ios version (delete or set default)
#         # ios_version = parse_config(section='ios_device', option='ios_version', config_file='mobile_config.ini')
#         # if ios_version == 'env_variable':
#         #     if os.environ.get('ios_version'):
#         #         ios_version = os.environ.get('ios_version')
#         #     else:
#         #         raise ValueError("The ios_version variable is not set in mobile_config.ini or environment variable")
#         # IOS_APP.update(app=ipa_path, platformVersion=ios_version, udid=udid, deviceName=udid)
#         IOS_APP.update(app=ipa_path, udid=udid, deviceName=udid)
#
#     DR_MOBILE.update(command_executor=COMMAND_EXECUTOR, desired_capabilities=IOS_APP)
