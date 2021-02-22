from common._libs.helpers.singleton import Singleton, delete_singleton_object, get_singleton_instance
from common.config_parser.config_dto import MobileDriverSettingsDTO
from common.config_parser.config_error import ConfigError
from appium.webdriver import Remote


class MobileDriver(metaclass=Singleton):

    def __init__(self, config: MobileDriverSettingsDTO, driver=Remote):
        self.config = config
        mobile_driver_settings = self._get_driver_settings(self.config)
        self.driver = driver(**mobile_driver_settings)
        self.driver.implicitly_wait(self.config.implicit_wait_time)

    @staticmethod
    def _get_driver_settings(settings):
        capabilities = dict(newCommandTimeout='18000',
                            noReset=False)
        if settings.platform == "ios":
            if settings.ipa_path and settings.ios_udid:
                capabilities.update(platformName='iOS')
                capabilities.update(automationName='XCUITest')
                capabilities.update(app=settings.ipa_path)
                capabilities.update(udid=settings.ios_udid, deviceName=settings.ios_udid)
            else:
                raise ConfigError(f"Can't use iOS platform without 'ipa_path' and 'ios_udid' parameters.")
        else:
            if settings.android_udid and settings.android_package and settings.android_activity:
                capabilities.update(platformName='Android')
                capabilities.update(automationName='UiAutomator2')
                capabilities.update(deviceName=settings.android_udid, udid=settings.android_udid)
                capabilities.update(appPackage=settings.android_package, appActivity=settings.android_activity)
            else:
                raise ConfigError(f"Can't use Android platform without "
                                  f"'android_udid, android_package, android_activity' parameters.")
        return dict(command_executor='http://127.0.0.1:4723/wd/hub', desired_capabilities=capabilities)

    def quit(self):
        self.driver.close_app()
        self.driver.quit()
        delete_singleton_object(MobileDriver)

    def restart_mobile_driver(self, config: MobileDriverSettingsDTO):
        self.quit()
        MobileDriver(config)


def get_mobile_driver_session() -> MobileDriver:
    session = get_singleton_instance(MobileDriver)
    if not isinstance(session, MobileDriver):
        raise ConnectionError("MobileDriver session was not created")
    return session
