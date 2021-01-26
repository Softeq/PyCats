import logging

from common._libs.helpers.singleton import Singleton, get_singleton_instance, delete_singleton_object
from common.config_manager import ConfigManager

from selenium.webdriver import Remote, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


class WebDriver(metaclass=Singleton):

    def __init__(self, config: ConfigManager, driver=Remote):
        self._settings = config.get_webdriver_settings()
        self.driver = driver(**self._get_driver_settings(self._settings))
        self.driver.implicitly_wait(self._settings.webdriver_implicit_wait_time)

        self.action_chains = ActionChains(self.driver)
        self.driver_wait = WebDriverWait

    @staticmethod
    def _get_driver_settings(settings):
        browser = dict(browserName=settings.browser,
                       version='',
                       platform='ANY')
        return dict(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=browser)

    def quit(self):
        self.driver.close()
        self.driver.quit()
        delete_singleton_object(WebDriver)

    def open_new_tab(self):
        """ Open new tab on existent webdriver session """
        self.driver.execute_script("window.open('');")
        self.switch_to_tab(tab_number=-1)

    def switch_to_tab(self, tab_number: int = 0):
        """ Switch to browser tab by index"""
        self.driver.switch_to.window(self.driver.window_handles[tab_number])


def get_webdriver_session() -> WebDriver:
    session = get_singleton_instance(WebDriver)
    if not isinstance(session, WebDriver):
        raise ConnectionError("WebDriver connection was not opened")
    return session


def start_webdriver_session(config: ConfigManager):
    """ Create webdriver session and maximize browser window """
    session = WebDriver(config)
    session.driver.maximize_window()


def stop_webdriver_session():
    """ stop webdriver session and delete session instance """
    get_webdriver_session().quit()


def navigate_to(url: str):
    """ Open {url} address in active webdriver session """
    logger.info(f"Navigate to {url}")
    get_webdriver_session().driver.get(url)


def close_cookie_consent():
    accept_button = get_webdriver_session().driver.find_element(by=By.XPATH, value="//button[@title='Accept']")
    accept_button.click()


def open_new_tab():
    get_webdriver_session().driver.execute_script("window.open('');")
    switch_to_tab(tab_number=-1)


def switch_to_tab(tab_number=0):
    driver = get_webdriver_session().driver
    driver.switch_to.window(driver.window_handles[tab_number])
