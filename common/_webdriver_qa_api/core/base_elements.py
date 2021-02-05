import time
import logging
from typing import Optional, Union, Dict

from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

from common._webdriver_qa_api.core.utils import assert_should_be_equal, assert_should_be_not_equal, \
    assert_should_contain, assert_should_not_contain, assert_should_be_greater_than, get_wait_seconds
from common._webdriver_qa_api.core.selenium_dynamic_elements import DynamicElement, DynamicElements
from common._webdriver_qa_api.mobile.mobile_driver import MobileDriver
from common._webdriver_qa_api.web.web_driver import WebDriver

logger = logging.getLogger(__name__)
TimeoutType = Optional[Union[int, float]]
WebDriverType = Optional[Union[WebDriver, MobileDriver]]


class BaseElement:

    def __init__(self, locator_type, locator, web_driver: WebDriverType, name=None, parent=None):
        self.locator_type = locator_type
        self.locator = locator
        self.driver = web_driver.driver
        self.parent = parent
        self.name = locator if name is None else name
        self.ALLOWED_DYNAMIC_METHODS = None
        self.element = DynamicElement(locator_type=locator_type,
                                      locator=locator,
                                      driver=self.driver, name=name,
                                      parent=parent)
        self.config = web_driver.config

    def __getattr__(self, item):
        if self.ALLOWED_DYNAMIC_METHODS is not None:
            assert item in self.ALLOWED_DYNAMIC_METHODS, f"get attribute {item} directly is forbidden"
        return getattr(self.element, item)

    def assert_present(self, is_present: bool = True, timeout: TimeoutType = None):
        """
        assert element present, test fails if expected state isn't equal to actual
        :param is_present: if true - should be present, if false - should be absent
        :param timeout: timeout in seconds, if not pass - find element with implicitly wait timeout
        """
        actual_state = self.is_present_without_waiting
        assert_should_be_equal(actual_value=actual_state, expected_value=is_present, timeout=timeout,
                               message=f"Verify is element '{self.name}' present state is '{is_present}'")

    def assert_enabled(self, is_enabled: bool = True, timeout: TimeoutType = None):
        """
        assert element enabled, test fails if expected state isn't equal to actual
        :param is_enabled: if true - should be enabled, if false - should be disabled
        :param timeout: timeout in seconds
        """
        actual_state = self.element.is_enabled
        assert_should_be_equal(actual_value=actual_state, expected_value=is_enabled, timeout=timeout,
                               message=f"Verify is element '{self.name}' enabled state is '{is_enabled}'")

    def assert_visible(self, is_visible: bool = True, timeout: TimeoutType = None):
        """
        assert element visible, test fails if expected state isn't equal to actual
        :param is_visible: if true - should be visible, if false - should be hidden
        :param timeout: timeout in seconds
        """
        actual_state = self.element.is_displayed
        assert_should_be_equal(actual_value=actual_state, expected_value=is_visible, timeout=timeout,
                               message=f"Verify is element '{self.name}' visible state is '{is_visible}'")

    def assert_focused(self, is_focused: bool = True):
        """
        assert element focused, test fails if expected state isn't equal to actual
        :param is_focused: if true - should be focused, if false - not focused
        """
        expected_state = "true" if is_focused else "false"
        actual_state = self.element.get_attribute("focused")
        assert_should_be_equal(actual_value=actual_state, expected_value=expected_state,
                               message="Verify is element '{}' focused".format(self.name))

    def assert_element_text(self, expected: str, timeout: TimeoutType = None):
        """
        assert that element text is equal to expected
        :param expected: expected element text value
        :param timeout: timeout in seconds
        """
        element_text = self.element.text
        assert_should_be_equal(actual_value=element_text, expected_value=expected, timeout=timeout,
                               message=f"Verify element '{self.name}' text, expected - '{expected}'")

    def assert_element_attribute(self, attribute, expected_value):
        """
        assert that element attribute is equal to expected
        """
        attribute_value = self.element.get_attribute(attribute)
        assert_should_be_equal(actual_value=attribute_value, expected_value=expected_value,
                               message=f"Verify '{attribute}' value of '{self.name}' element")

    def assert_element_contains_text(self, expected: str, timeout: TimeoutType = None):
        """
        assert that element text contains expected value {expected}
        :param expected: expected text value
        :param timeout: timeout in seconds
        """
        assert_should_contain(actual_value=expected, expected_value=self.get_element_text, timeout=timeout,
                              message=f"Verify element '{self.name}' contains '{expected}' text")

    def assert_element_should_not_contain_text(self, expected: str):
        """
        assert that element text contains expected value {expected}
        """
        element_text = self.element.text
        assert_should_not_contain(actual_value=expected,
                                  expected_value=element_text,
                                  message=f"Verify element '{self.name}' should not contains '{expected}' text")

    def assert_element_text_empty(self, timeout: TimeoutType = None):
        """
        assert that element text is empty (equals with empty string)
        :param timeout: timeout in seconds
        """
        self.assert_element_text(expected="", timeout=timeout)

    def assert_element_text_not_empty(self, timeout: TimeoutType = None):
        """
        assert that element text is not empty (equals with empty string)
        :param timeout: timeout in seconds
        """
        element_text = self.element.text
        assert_should_be_not_equal(actual_value=element_text, expected_value="", timeout=timeout,
                                   message=f"Verify {self.name} element text is not empty")

    def is_present(self) -> bool:
        """
        :return: true if element is present, false if element is absent
        """
        try:
            self.element()
        except NoSuchElementException:
            return False
        return True

    def is_present_without_waiting(self) -> bool:
        """
        :return: true if element is present, false if element is absent
        """
        try:
            self.driver.implicitly_wait(0)
            return self.is_present()
        finally:
            self.driver.implicitly_wait(self.config.implicit_wait_time)

    def _wait_element(self, timeout: Union[int, float]):
        """
        wait for element present

        :param timeout: number of seconds after which test will fail if element is absent.
        """
        try:
            self.driver.implicitly_wait(timeout)
            return self.is_present()
        finally:
            self.driver.implicitly_wait(self.config.implicit_wait_time)

    def wait_element(self, timeout: TimeoutType = None):
        """
        wait for element present with fail test if element not be found
        :param timeout: number of seconds after which test will fail if element is absent.
        """
        second = get_wait_seconds(timeout, self.config)
        assert_should_be_equal(actual_value=self._wait_element(timeout=second), expected_value=True,
                               message=f"Wait for element {self.name} in {second} seconds")

    def try_wait_element(self, timeout: TimeoutType = None) -> bool:
        """
        wait to see if element becomes present during timeout
        :param timeout: number of seconds after which test will fail if element is absent.
        :return: true if element becomes present during timeout
        """
        second = get_wait_seconds(timeout, self.config)

        logger.info("Try to get element '{0}' in {1} seconds".format(self.name, timeout))
        return self._wait_element(second)

    def wait_element_absent(self, timeout: TimeoutType = None):
        """
        wait for element absent (if timeout more than 20 second, find element with default timeout,
         else find element every 0.1 seconds)
        :param timeout: number of seconds after which test will wail if element is absent.
        """
        second = get_wait_seconds(timeout, self.config)

        logger.info("Wait for '{0}' absent in {1} seconds".format(self.name, 0 if not second else second))
        end_time = time.time() + second
        present = True
        while time.time() < end_time and present:
            present = self.is_present_without_waiting()
            time.sleep(0.1)
        self.assert_present(is_present=False)

    def wait_element_enabled(self, timeout: TimeoutType = None):
        """
        wait for element enabled
        :param timeout: number of seconds after which test will wail if element is enabled.
        """
        second = get_wait_seconds(timeout, self.config)
        logger.info(f"Wait for '{self.name}' is enabled in '{second}' seconds")
        self.assert_enabled(is_enabled=True, timeout=second)

    def wait_element_disabled(self, timeout: TimeoutType = None):
        """
        wait for element disabled
        :param timeout: number of seconds after which test will wail if element is enabled.
        """
        second = get_wait_seconds(timeout, self.config)
        logger.info(f"Wait for '{self.name}' is disabled in '{second} seconds'")
        self.assert_enabled(is_enabled=False, timeout=second)

    def wait_element_visible(self, timeout: TimeoutType = None):
        """
        wait for element visible
        :param timeout: number of seconds after which test will wail if element is visible.
        """
        second = get_wait_seconds(timeout, self.config)
        logger.info(f"Wait for '{self.name}' is visible in '{second}' seconds")
        self.assert_visible(is_visible=True, timeout=second)

    def wait_element_invisible(self, timeout: TimeoutType = None):
        """
        wait for element invisible
        :param timeout: number of seconds after which test will wail if element is visible.
        """
        second = get_wait_seconds(timeout, self.config)
        logger.info(f"Wait for '{self.name}' is invisible in '{second}' seconds")
        self.assert_visible(is_visible=False, timeout=second)

    def wait_element_contains_text(self, expected: str, timeout: TimeoutType = None):
        """
        wait for element invisible
        :param expected: expected text value
        :param timeout: number of seconds after which test will wail if element is visible.
        """
        second = get_wait_seconds(timeout, self.config)
        logger.info(f"Wait for '{self.name}' contains following text: '{expected}' "
                    f"in '{second}' seconds")

        end_time = time.time() + second
        while time.time() < end_time and expected not in self.element.text:
            time.sleep(0.2)
        self.assert_element_contains_text(expected)

    def wait_element_does_not_contain_text(self, expected: str, timeout: TimeoutType = None):
        """
        wait for element invisible
        :param expected: text that should not be a part of element text
        :param timeout: number of seconds after which test will wail if element is visible.
        """
        second = get_wait_seconds(timeout, self.config)
        logger.info(f"Wait for '{self.name}' does not contain following text: '{expected}' "
                    f"in '{second}' seconds")

        end_time = time.time() + second
        while time.time() < end_time and expected in self.element.text:
            time.sleep(0.2)
        self.assert_element_should_not_contain_text(expected)

    def get_element_text(self) -> str:
        """
        find element and get it's text
        :return: Text of element
        """
        logger.info(f"Get text of element '{self.name}'")
        return self.element.text

    def get_element_location(self) -> Dict[int, str]:
        """
        find element and get it's location
        :return: location of element in format: {'x': 606, 'y': 126}
        """
        logger.info(f"Get location of element '{self.name}'")
        return self.element.location

    def click_by_mouse_target(self):
        """
        Click to element using mouse click action:
            move target to element -> click
        """
        action = ActionChains(self.driver)
        action.move_to_element_with_offset(self.element, 5, 5)
        action.click()
        action.perform()


class BaseElements:
    def __init__(self, locator_type, locator, web_driver, name=None, parent=None):
        self.locator_type = locator_type
        self.locator = locator
        self.driver = web_driver.driver
        self.elements = DynamicElements(locator_type=locator_type,
                                        locator=locator,
                                        driver=self.driver,
                                        name=name,
                                        parent=parent)

    def assert_elements_number_greater_than(self, expected):
        actual = len(self.elements())
        assert_should_be_greater_than(actual, expected)

    def get_elements_text(self):
        """
        find elements and get it's text
        :return: list of the text of element
        """
        return [element.text for element in self.elements.selenium_element]

    def get_elements(self):
        """
        find elements and get it's text
        :return: list of selenium elements
        """
        return self.elements.selenium_element
