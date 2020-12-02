import random

from selenium.common.exceptions import WebDriverException

from common._webdriver_qa_api.core.base_pages import BasePage
from common._webdriver_qa_api.core.utils import fail_test
from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.mobile_driver import MobileDriver
from common.config_manager import ConfigManager
from common.facade import logger


class MobilePage(BasePage):
    def __init__(self, locator_type, locator, name, should_present=True):
        config = ConfigManager()
        super().__init__(driver=MobileDriver(config).driver, config=config,
                         locator_type=locator_type, locator=locator, name=name)
        if should_present:
            self.wait_page_present()

    def get_page_source(self):
        """
        :return: width of the page
        """
        return self.driver.page_source

    def get_page_width(self):
        """
        :return: width of the page
        """
        return self.driver.get_window_size()['width']

    def get_page_height(self):
        """
        :return: height of the page
        """
        return self.driver.get_window_size()['height']

    def scroll_page_down(self):
        """
        scroll page down to the bottom, only works on iOS
        """
        self.driver.execute_script("mobile: scroll", {"direction": 'down'})
        return self

    def scroll_page_up(self):
        """
        scroll page up to the top, only works on iOS
        """
        self.driver.execute_script("mobile: scroll", {"direction": 'up'})
        return self

    def hide_keyboard(self):
        """
        hide keyboard, only works on Android
        """
        try:
            self.driver.hide_keyboard()
        except WebDriverException as e:
            if "Soft keyboard not present, cannot hide keyboard" in str(e):
                pass
            else:
                raise e
        return self

    def hide_keyboard_by_tap(self):
        """
        try to hide keyboard by tapping somewhere on page
        """
        self.tap_by_coordinates(1, self.get_page_height() / 2)

    def swipe_down(self, start_coord_x=None, start_coord_y=None, duration=300, silent=False):
        """
        perform swipe from given coordinates to the top to scroll to the bottom part of the page
        :param start_coord_y: y coordinate to start swipe
        :param start_coord_x: x coordinate to start swipe
        :param duration: time to take the swipe, in ms
        :param silent: true - log message isn't displayed, false - log message is displayed
        """
        if not silent:
            logger.info('Swiping in direction to the bottom part of the page')
        start_x = round(self.get_page_width() / 2) if not start_coord_x else start_coord_x
        start_y = round(self.get_page_height() / 2) if not start_coord_y else start_coord_y
        offset_y = round(self.get_page_height() / 8)
        result_y = 1 if (start_y - offset_y) < 0 else start_y - offset_y
        return self.swipe(start_x, start_y, start_x, result_y, duration)

    def swipe_up(self, start_coord_x=None, start_coord_y=None, duration=300, offset=0.25, silent=False):
        """
        perform swipe from given coordinates to the bottom to scroll to the top part of the page
        :param start_coord_y: y coordinate to start swipe
        :param start_coord_x: x coordinate to start swipe
        :param duration: time to take the swipe, in ms
        :param offset: offset ratio (0.5 - half of page, 0 - no swiping)
        :param silent: true - log message isn't displayed, false - log message is displayed
        """
        if not silent:
            logger.info('Swiping in direction to the top part of the page')
        start_x = round(self.get_page_width() / 2) if not start_coord_x else start_coord_x
        start_y = round(self.get_page_height() / 2) if not start_coord_y else start_coord_y
        offset_y = round(self.get_page_height() * offset)
        result_y = self.get_page_height() - 1 if start_y + offset_y > self.get_page_height() else start_y + offset_y
        return self.swipe(start_x, start_y, start_x, result_y, duration)

    def swipe_left(self, start_coord_x=None, start_coord_y=None, duration=300, silent=False):
        """
        perform swipe from given coordinates to the left side of page to scroll to the left part of the page
        :param start_coord_y: y coordinate to start swipe
        :param start_coord_x: x coordinate to start swipe
        :param duration: time to take the swipe, in ms
        :param silent: true - log message isn't displayed, false - log message is displayed
        """
        if not silent:
            logger.info('Swiping in direction to the left part of the page')
        start_x = round(self.get_page_width() / 4) * 3 if not start_coord_x else start_coord_x
        start_y = round(self.get_page_height() / 2) if not start_coord_y else start_coord_y
        offset_x = round(self.get_page_width() / 2)
        result_x = 1 if start_x - offset_x < 0 else start_x - offset_x
        return self.swipe(start_x, start_y, result_x, start_y, duration)

    def swipe_right(self, start_coord_x=None, start_coord_y=None, duration=300, silent=False):
        """
        perform swipe from given coordinates to the right side of page to scroll to the right part of the page
        :param start_coord_y: y coordinate to start swipe
        :param start_coord_x: x coordinate to start swipe
        :param duration: time to take the swipe, in ms
        :param silent: true - log message isn't displayed, false - log message is displayed
        """
        if not silent:
            logger.info('Swiping in direction to the right part of the page')
        start_x = round(self.get_page_width() / 4) if not start_coord_x else start_coord_x
        start_y = round(self.get_page_height() / 2) if not start_coord_y else start_coord_y
        offset_x = round(self.get_page_width() / 2)
        result_x = self.get_page_width() - 1 if start_x + offset_x > self.get_page_width() else start_x + offset_x
        return self.swipe(start_x, start_y, result_x, start_y, duration)

    def swipe(self, start_x, start_y, x_offset, y_offset, duration=None):
        """
        swipe page and catch exception if it appears.
        appium issue https://github.com/appium/appium/issues/7572
        :param start_x: x coordinate to start swipe
        :param start_y: y coordinate to start swipe
        :param x_offset: x coordinate to swipe right (>0) or left (<0) from start_x
        :param y_offset: y coordinate to swipe down (>0) or up (<0) from start_y
        :param duration: time to take the swipe, in ms
        """
        try:
            self.driver.swipe(start_x, start_y, x_offset, y_offset, duration)
        except WebDriverException:
            logger.info("Swipe failed the first time because of WebDriverAgent error. Trying to swipe again")
            self.driver.swipe(start_x, start_y, x_offset, y_offset, duration)
        return self

    def scroll_to_element_if_needed(self, element, top_limit=None, bottom_limit=None, silent=False):
        """
        If element is not fully on screen, scroll in the corresponding direction to make it fully visible
        :param element: mobile element to scroll to
        :param top_limit: Y coordinate that should be above element
        :param bottom_limit: value of Y coordinate that should be below element (page size - bottom_limit)
        :param silent: true - log message isn't displayed, false - log message is displayed
        """
        if not silent:
            logger.info('Scroll to element {}'.format(element.name))
        top = top_limit if top_limit and top_limit >= 0 else 0
        if bottom_limit and bottom_limit <= self.get_page_height():
            bottom = self.get_page_height() - bottom_limit
        else:
            bottom = self.get_page_height()
        attempt = 0
        while attempt < 5:
            if element.get_bottom_y() > bottom:
                self.swipe_down(silent=silent)
            elif element.get_top_y() < top:
                self.swipe_up(silent=silent)
            else:
                return True
            attempt += 1

    def scroll_to_element_in_direction(self, element, direction, silent=False):
        """
        If element is not fully on screen, scroll in the corresponding direction to make it fully visible
        :param element: mobile element to scroll to
        :param direction: swipe direction: up / down
        :param silent: true - log message isn't displayed, false - log message is displayed
        """
        assert direction in ["up", "down"], "Direction value should be in [up, down] list, actual value - {}"
        swipe_action = self.swipe_down if direction == 'down' else self.swipe_up

        if not silent:
            logger.info('Scroll to element {}'.format(element.name))
        attempt = 0
        while attempt < 5:
            if element.is_present():
                return None
            swipe_action(silent=silent)
            attempt += 1

    def tap_by_coordinates(self, x, y):
        """
        tap on coordinates
        :param x: x coordinate to tap
        :param y: y coordinate to tap
        """
        logger.info("Tap to coordinates (x,y) - ({x},{y})".format(x=x, y=y))
        self.driver.tap([(x, y)])

    def tap_and_hold_by_coordinates(self, x, y, seconds=3):
        """
        tap on coordinates and hold (seconds) time
        :param x: x coordinate to tap
        :param y: y coordinate to tap
        """
        logger.info("Click and hold coordinates ({0},{1}) for a {2} seconds".format(x, y, seconds))
        self.driver.tap([(x, y)], seconds * 1000)

    def wait_page_present(self, seconds=30):
        """
        wait for page to appear
        """
        element = MobileElement(self.locator_type, self.locator, self.name)
        if not element.try_wait_element(silent=True, second=seconds):
            fail_test("Page '{0}' was not opened in {1} seconds".format(self.name, seconds))
        logger.info("Page '{0}' was opened".format(self.name))

    def monkey_actions(self, actions_count=100):
        """
        Do one of the next actions: [swipe, click, click_and_hold] for a {count} times for emulating monkey with device
        :param actions_count: count of actions that will be performed on the page
        """
        def _get_random_point_on_screen():
            x = random.randint(1, self.get_page_width())
            y = random.randint(1, self.get_page_height())
            point = (x, y)
            return point

        list_of_actions = [self.tap_by_coordinates, self.swipe, self.tap_and_hold_by_coordinates]
        list_of_swipes = [self.swipe_down, self.swipe_up, self.swipe_left, self.swipe_right]

        for index in range(actions_count):
            action = random.choice(list_of_actions)
            if action == self.swipe:
                action = random.choice(list_of_swipes)
            logger.info("Monkey action {0}/{1}: {2} action".format(index, actions_count, action.__name__))
            action(*_get_random_point_on_screen())
