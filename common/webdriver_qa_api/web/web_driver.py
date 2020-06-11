from selenium.webdriver import Remote, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from common.scaf import  get_logger, config

logger = get_logger(__name__)


class WebDriver:
    web_driver = None

    def __init__(self, driver=Remote):
        self.driver = driver(**self._get_driver_settings())
        self.driver.implicitly_wait(config.web_settings.webdriver_implicit_wait_time)

        WebDriver.web_driver = self.driver
        self.action_chains = ActionChains(self.driver)
        self.driver_wait = WebDriverWait

    @staticmethod
    def _get_driver_settings():
        browser = dict(browserName=config.web_settings.browser,
                       version='',
                       platform='ANY')
        return dict(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=browser)

    @staticmethod
    def quit():
        if WebDriver.web_driver:
            WebDriver.web_driver.close()
            WebDriver.web_driver.quit()
            WebDriver.web_driver = None


def start_webui():
    WebDriver().web_driver.fullscreen_window()


def stop_webui():
    WebDriver.quit()


def navigate_to(url):
    logger.info(f"Navigate to {url}")
    WebDriver.web_driver.get(url)


def close_cookie_consent():
    accept_button = WebDriver.web_driver.find_element(by=By.XPATH, value="//button[@title='Accept']")
    accept_button.click()
