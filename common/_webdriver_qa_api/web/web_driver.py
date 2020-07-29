import logging

from common.config_manager import ConfigManager

from selenium.webdriver import Remote, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


class WebDriver:
    web_driver = None

    def __init__(self, config: ConfigManager, driver=Remote):
        self._settings = config.get_webdriver_settings()
        self.driver = driver(**self._get_driver_settings(self._settings))
        self.driver.implicitly_wait(self._settings.webdriver_implicit_wait_time)

        WebDriver.web_driver = self.driver
        self.action_chains = ActionChains(self.driver)
        self.driver_wait = WebDriverWait

    @staticmethod
    def _get_driver_settings(settings):
        browser = dict(browserName=settings.browser,
                       version='',
                       platform='ANY')
        return dict(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=browser)

    @staticmethod
    def quit():
        if WebDriver.web_driver:
            WebDriver.web_driver.close()
            WebDriver.web_driver.quit()
            WebDriver.web_driver = None


def start_webui(config: ConfigManager):
    WebDriver(config).web_driver.maximize_window()


def stop_webui():
    WebDriver.quit()


def navigate_to(url):
    logger.info(f"Navigate to {url}")
    WebDriver.web_driver.get(url)


def close_cookie_consent():
    accept_button = WebDriver.web_driver.find_element(by=By.XPATH, value="//button[@title='Accept']")
    accept_button.click()
