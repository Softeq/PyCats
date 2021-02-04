import logging
from typing import Union

from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import WebDriverException

from common._webdriver_qa_api.core.base_elements import BaseElement, BaseElements
from common._webdriver_qa_api.core.text_box_mixin import TextBoxActionsMixin
from common._webdriver_qa_api.mobile.mobile_driver import get_mobile_driver_session
from common.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class MobileElements(BaseElements):
    def __init__(self, locator_type, locator, name=None, parent=None):
        super().__init__(locator_type, locator, driver=get_mobile_driver_session().driver, name=name, parent=parent)


class MobileElement(BaseElement):
    def __init__(self, locator_type, locator, name=None, parent=None, scroll=False):
        config = ConfigManager()
        super().__init__(driver=get_mobile_driver_session().driver, config=config,
                         locator_type=locator_type, locator=locator,
                         name=name, parent=parent)
        self.scroll = scroll

    def get_element_size(self) -> dict:
        """
        get size (x - 'width' and y - 'height') of the element: {'height': int, 'width': int}
        """
        return self.element().size

    def click_and_hold(self, timeout: Union[int, float]):
        """
        Click and hold element for a <seconds> seconds
        :param timeout: hold time in seconds
        """
        logger.info(f"Click and hold '{self.name}' for a {timeout} seconds")

        element = self.get_element()
        actions = TouchAction(self.driver)
        actions.long_press(element, duration=timeout * 1000)
        actions.release()
        actions.perform()

    def click_multiple_times(self, times: int):
        """
        Click element multiple times
        :param: times: click action count
        """
        logger.info(f"Click '{self.name}' for a {times} times")

        element = self.get_element()
        for loop in range(times):
            logger.info(f"Click: {loop + 1}/{times}")
            element.click()

    def get_top_y(self) -> int:
        """
        Get Y coordinate of Top edge of the element
        :return: Y coordinate of element's Top point
        """
        return self.get_element_location()['y']

    def get_bottom_y(self) -> int:
        """
        Get Y coordinate of Bottom edge of the element
        :return: Y coordinate of element's Bottom point
        """
        return self.get_top_y() + self.get_element_size()['height']


class MobileTextBox(TextBoxActionsMixin, MobileElement):

    def set_text(self, text: str, skip_if_none: bool = True):
        """
        clear the text field and type new text
        catch exception if it appears (appium issue https://github.com/appium/appium/issues/7572)
        :param text: text that should be set
        :param skip_if_none: true - do nothing if text isn't specified, set text if it specified
        false - set text if it specified, error if text isn't specified
        """
        try:
            super().set_text(text, skip_if_none)
        except WebDriverException:
            logger.info("Set Text failed the first time because of WebDriverAgent error. Trying to set text again")
            super().set_text(text, skip_if_none)
        return self
