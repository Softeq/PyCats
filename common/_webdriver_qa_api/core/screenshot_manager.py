import os
import shutil

from selenium.webdriver.remote.webdriver import WebDriver

from common._libs.helpers.os_helpers import get_timestamp, create_folder
from common._libs.helpers.utils import slugify
from common._webdriver_qa_api.mobile.mobile_driver import get_mobile_driver_session
from common._webdriver_qa_api.web.web_driver import get_webdriver_session


class ScreenShot:

    base_screenshots_folder = os.path.join(os.getcwd(), 'temp_screenshots')

    def __init__(self, driver: WebDriver, screen_path: str = None):
        self.driver = driver
        self.screenshot_folder = screen_path if screen_path else self.base_screenshots_folder

    def __del__(self, *args, **kwargs):
        if os.path.exists(self.base_screenshots_folder):
            shutil.rmtree(self.base_screenshots_folder)

    def save_screenshot(self, screenshot_name: str = None) -> str:
        """
        Save screenshot with name <current_timestamp>.png
        :param screenshot_name: name of the screenshot that should be saved
        :return: path to image file
        """
        screenshot_name = get_timestamp() if not screenshot_name else slugify(screenshot_name)
        create_folder(self.screenshot_folder)

        full_path = os.path.join(self.screenshot_folder, screenshot_name + '.png')
        self.driver.save_screenshot(full_path)
        return full_path


class WebScreenShot(ScreenShot):

    def __init__(self, screen_path: str = None):
        super().__init__(get_webdriver_session().driver, screen_path)


class MobileScreenShot(ScreenShot):

    def __init__(self, screen_path: str = None):
        super().__init__(get_mobile_driver_session().driver, screen_path)
