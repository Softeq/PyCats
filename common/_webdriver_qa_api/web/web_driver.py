import logging

from common._libs.helpers.singleton import Singleton, get_singleton_instance, delete_singleton_object

from selenium import webdriver
from selenium.webdriver import Remote, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from common.config_parser.config_dto import WebDriverSettingsDTO

logger = logging.getLogger(__name__)


class WebDriver(metaclass=Singleton):

    def __init__(self, config: WebDriverSettingsDTO, driver=Remote):
        self.config = config
        self.driver = driver(**self._get_driver_settings(self.config))
        self.driver.implicitly_wait(self.config.implicit_wait_time)

        self.action_chains = ActionChains(self.driver)
        self.driver_wait = WebDriverWait

    @staticmethod
    def _get_driver_settings(settings):
        browser = dict(browserName=settings.browser,
                       version='',
                       platform='ANY')
        options = None
        if settings.browser == "chrome" and settings.chrome_options:
            options = webdriver.ChromeOptions()
            for chrome_option in settings.chrome_options:
                options.add_argument(chrome_option)
        return dict(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=browser, options=options)

    def quit(self):
        self.driver.close()
        self.driver.quit()
        delete_singleton_object(WebDriver)


def get_webdriver_session() -> WebDriver:
    session = get_singleton_instance(WebDriver)
    if not isinstance(session, WebDriver):
        raise ConnectionError("WebDriver connection was not opened")
    return session


def start_webdriver_session(config: WebDriverSettingsDTO):
    """ Create webdriver session and maximize browser window """
    logger.info("Start WebDriver session")
    session = WebDriver(config)
    session.driver.maximize_window()


def stop_webdriver_session():
    """ stop webdriver session and delete session instance """
    logger.info("Stop WebDriver session")
    get_webdriver_session().quit()


def navigate_to(url: str):
    """ Open {url} address in active webdriver session """
    logger.info(f"Navigate to {url}")
    get_webdriver_session().driver.get(url)


def close_cookie_consent():
    accept_button = get_webdriver_session().driver.find_element(by=By.XPATH, value="//button[@title='Accept']")
    accept_button.click()


def open_new_tab():
    """ Open new tab on existent webdriver session """
    logger.info(f"Open new tab.")
    get_webdriver_session().driver.execute_script("window.open('');")
    switch_to_tab(tab_number=-1)


def switch_to_tab(tab_number=0):
    """ Switch to browser tab by index"""
    logger.info(f"Switch to tab - {tab_number}")
    driver = get_webdriver_session().driver
    driver.switch_to.window(driver.window_handles[tab_number])
