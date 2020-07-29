import time
import logging

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from common.config_manager import ConfigManager
from common._webdriver_qa_api.core.utils import assert_should_be_equal, fail_test, assert_should_be_not_equal, \
    assert_should_contain, assert_should_not_contain, assert_should_be_greater_than, get_wait_seconds
from common._webdriver_qa_api.core.selenium_dynamic_elements import DynamicElement, DynamicElements

logger = logging.getLogger(__name__)


class BaseElement:

    def __init__(self, locator_type, locator, driver, config: ConfigManager, name=None, parent=None):
        self.locator_type = locator_type
        self.locator = locator
        self.driver = driver
        self.parent = parent
        self.name = locator if name is None else name
        self.ALLOWED_DYNAMIC_METHODS = None
        self.element = DynamicElement(locator_type=locator_type,
                                      locator=locator,
                                      driver=driver, name=name,
                                      parent=parent)
        self._webdriver_settings = config.get_webdriver_settings()

    def __getattr__(self, item):
        if self.ALLOWED_DYNAMIC_METHODS is not None:
            assert item in self.ALLOWED_DYNAMIC_METHODS, f"get attribute {item} directly is forbidden"
        return getattr(self.element, item)

    def assert_present(self, is_present=True, with_waiting=True):
        """
        assert element present, test fails if expected state isn't equal to actual
        :param is_present: if true - should be present, if false - should be absent
        :param with_waiting: if true - find element using is_present() method (with implicitly wait timeout),
                             if false - find element using is_present_without_waiting() method (without timeout)
        """
        actual_state = self.is_present() if with_waiting else self.is_present_without_waiting()
        assert_should_be_equal(actual_value=actual_state, expected_value=is_present,
                               message=f"Verify is element '{self.name}' present on the page")

    def assert_enabled(self, is_enabled=True):
        """
        assert element enabled, test fails if expected state isn't equal to actual
        :param is_enabled: if true - should be enabled, if false - should be disabled
        """
        actual_state = self.element.is_enabled()
        assert_should_be_equal(actual_value=actual_state, expected_value=is_enabled,
                               message="Verify is element '{}' "
                                       "enabled {}".format(self.name, is_enabled))

    def assert_visible(self, is_visible=True):
        """
        assert element visible, test fails if expected state isn't equal to actual
        :param is_visible: if true - should be visible, if false - should be hidden
        """
        actual_state = self.element.is_displayed()
        assert_should_be_equal(actual_value=actual_state,
                               expected_value=is_visible,
                               message="Verify is element '{}' "
                                       "visible".format(self.name))

    def assert_focused(self, is_focused=True):
        """
        assert element focused, test fails if expected state isn't equal to actual
        :param is_focused: if true - should be focused, if false - not focused
        """
        expected_state = "true" if is_focused else "false"
        actual_state = self.element.get_attribute("focused")
        assert_should_be_equal(actual_value=actual_state, expected_value=expected_state,
                               message="Verify is element '{}' focused".format(self.name))

    def assert_element_text(self, expected):
        """
        assert that element text is equal to expected
        """
        element_text = self.element.text
        assert_should_be_equal(actual_value=element_text, expected_value=expected, silent=True)

    def assert_element_attribute(self, attribute, expected_value):
        """
        assert that element attribute is equal to expected
        """
        attribute_value = self.element.get_attribute(attribute)
        assert_should_be_equal(actual_value=attribute_value, expected_value=expected_value, silent=True)

    def assert_element_contains_text(self, expected):
        """
        assert that element text contains expected value {expected}
        """
        element_text = self.element.text
        assert_should_contain(actual_value=expected, expected_value=element_text, silent=True)

    def assert_element_should_not_contain_text(self, expected):
        """
        assert that element text contains expected value {expected}
        """
        element_text = self.element.text
        assert_should_not_contain(actual_value=expected,
                                  expected_value=element_text,
                                  silent=True)

    def assert_element_text_empty(self):
        """
        assert that element text is empty (equals with empty string)
        """
        self.assert_element_text("")

    def assert_element_text_not_empty(self):
        """
        assert that element text is not empty (equals with empty string)
        """
        element_text = self.element.text
        assert_should_be_not_equal(actual_value=element_text, expected_value="", silent=True)

    def is_present(self):
        """
        :return: true if element is present, false if element is absent
        """
        return self.element() is not None

    def is_present_without_waiting(self):
        """
        :return: true if element is present, false if element is absent
        """
        try:
            self.driver.implicitly_wait(0)
            WebDriverWait(self.driver, 0).until(EC.presence_of_element_located((self.locator_type, self.locator)))
            return True
        except:
            return False
        finally:
            self.driver.implicitly_wait(self._webdriver_settings.webdriver_implicit_wait_time)

    def _wait_element(self, silent=False, second=None):
        """
        wait for element present

        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will fail if element is absent.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        if not silent:
            logger.info("Wait for '{0}' in {1} seconds".format(self.name, second))
        wait = WebDriverWait(self.driver, second)
        wait.until(EC.presence_of_element_located((self.locator_type, self.locator)))
        return self

    def wait_element(self, silent=False, second=None):
        """
        wait for element present with fail test if element not be found
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will fail if element is absent.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        try:
            self._wait_element(silent, second)
        except TimeoutException:
            fail_test("The element {} can not be located in {} seconds".format(self.name, second))
        return self

    def try_wait_element(self, silent=False, second=None):
        """
        wait to see if element becomes present during timeout
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will fail if element is absent.
        :return: true if element becomes present during timeout
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        try:
            self._wait_element(silent, second)
        except TimeoutException:
            return False
        return True

    def wait_element_absent(self, silent=False, second=None):
        """
        wait for element absent (if timeout more than 20 second, find element with default timeout,
         else find element every 0.1 seconds)
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will wail if element is absent.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        present_method = self.is_present if second > 30 else self.is_present_without_waiting

        if not silent:
            logger.info("Wait for '{0}' absent in {1} seconds".format(self.name, second))
        end_time = time.time() + second
        present = True
        while time.time() < end_time and present:
            present = present_method()
            time.sleep(0.1)
        self.assert_present(is_present=False, with_waiting=False)

    def wait_element_enabled(self, silent=False, second=None):
        """
        wait for element enabled
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will wail if element is enabled.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        if not silent:
            logger.info("Wait for '{0}' is enabled".format(self.name))
        assert_should_be_equal(actual_value=self.element.is_enabled, expected_value=True,
                               message="Verify is element '{}' enabled".format(self.name),
                               timeout=second, silent=silent)

    def wait_element_disabled(self, silent=False, second=None):
        """
        wait for element disabled
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will wail if element is enabled.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        if not silent:
            logger.info("Wait for '{0}' is disabled".format(self.name))
        assert_should_be_equal(actual_value=self.element.is_enabled, expected_value=False,
                               message="Verify is element '{}' disabled".format(self.name),
                               timeout=second, silent=silent)

    def wait_element_visible(self, silent=False, second=None):
        """
        wait for element visible
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will wail if element is visible.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        if not silent:
            logger.info("Wait for '{0}' is visible".format(self.name))
        assert_should_be_equal(actual_value=self.element.is_displayed, expected_value=True,
                               message="Verify is element '{}' visible".format(self.name),
                               timeout=second, silent=silent)

    def wait_element_invisible(self, silent=False, second=None):
        """
        wait for element invisible
        :param silent: true - log message isn't displayed, false - log message is displayed
        :param second: number of seconds after which test will wail if element is visible.
        """
        second = get_wait_seconds(second, self._webdriver_settings)
        if not silent:
            logger.info("Wait for '{0}' is invisible".format(self.name))
        assert_should_be_equal(actual_value=self.element.is_displayed, expected_value=False,
                               message="Verify is element '{}' invisible".format(self.name),
                               timeout=second, silent=silent)

    def wait_element_contains_text(self, expected, second=None):
        second = get_wait_seconds(second, self._webdriver_settings)
        end_time = time.time() + second
        while time.time() < end_time and expected not in \
                self.element.text:
            pass
        self.assert_element_text(expected)

    def wait_element_does_not_contain_text(self, expected, second=None):
        second = get_wait_seconds(second, self._webdriver_settings)
        end_time = time.time() + second
        while time.time() < end_time and expected in self.element.text:
            pass
        self.assert_element_should_not_contain_text(expected)

    def get_element_location(self, silent=True):
        """
        find element and get it's location
        :param silent: true - log message isn't displayed, false - log message is displayed
        :return: location of element ('x' and 'y')
        """
        if not silent:
            logger.info("Get location of element '{}'".format(self.locator))
        return self.element.location

    def click_by_coord(self):
        action = ActionChains(self.driver)
        action.move_to_element_with_offset(self.element, 5, 5)
        action.click()
        action.perform()

    def wait_element_loaded(self, second=10):
        second = get_wait_seconds(second, self._webdriver_settings)
        wait = WebDriverWait(self.driver, second)
        try:
            wait.until(EC.staleness_of(self.element()))
        except TimeoutException:
            pass
        finally:
            wait.until(EC.visibility_of(self.element()))


class BaseElements:
    def __init__(self, locator_type, locator, driver, name=None, parent=None):
        self.locator_type = locator_type
        self.locator = locator
        self.driver = driver
        self.elements = DynamicElements(locator_type=locator_type,
                                        locator=locator,
                                        driver=driver,
                                        name=name,
                                        parent=parent)

    def assert_elements_number_greater_than(self, expected):
        actual = len(self.elements())
        assert_should_be_greater_than(actual, expected)


class BaseElementsActionsMixin:

    def get_elements_text(self):
        """
        find elements and get it's text
        :return: list of the text of element
        """
        result = []
        for element in self():
            result.append(element.text)
        return result
