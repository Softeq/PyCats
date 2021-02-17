import os
import shutil

from common._libs.helpers.os_helpers import get_timestamp, create_folder
from common._webdriver_qa_api.mobile.mobile_driver import get_mobile_driver_session
from common._webdriver_qa_api.web.web_driver import get_webdriver_session


class ScreenShot:

    BASE_SCREENSHOTS_FOLDER = os.path.join(os.getcwd(), 'temp_screenshots')

    def __init__(self, driver, screen_path=None):
        self.driver = driver
        self.screenshot_folder = screen_path if screen_path else self.BASE_SCREENSHOTS_FOLDER

    def __del__(self, *args, **kwargs):
        if os.path.exists(self.BASE_SCREENSHOTS_FOLDER):
            shutil.rmtree(self.BASE_SCREENSHOTS_FOLDER)

    def save_screenshot(self, screenshot_name=None):
        """
        Save screenshot with name <current_timestamp>.png
        :param screenshot_name: name of the screenshot that should be saved
        :return: path to image file
        """
        if not screenshot_name:
            screenshot_name = get_timestamp()
        create_folder(self.screenshot_folder)

        full_path = os.path.join(self.screenshot_folder, screenshot_name + '.png')
        self.driver.save_screenshot(full_path)
        return full_path


class WebScreenShot(ScreenShot):

    def __init__(self, screen_path=None):
        super().__init__(get_webdriver_session().driver, screen_path)


class MobileScreenShot(ScreenShot):

    def __init__(self, screen_path=None):
        super().__init__(get_mobile_driver_session().driver, screen_path)
