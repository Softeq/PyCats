from selenium.webdriver import ActionChains

from common._libs.config_manager import ConfigManager
from common._webdriver_qa_api.web.web_driver import WebDriver
from common._webdriver_qa_api.core.utils import assert_should_be_equal
from common._webdriver_qa_api.core.base_elements import BaseElement, BaseElements
from common._webdriver_qa_api.core.text_box_mixin import TextBoxActionsMixin


class WebElements(BaseElements):
    def __init__(self, locator_type, locator, name=None, parent=None):
        super().__init__(locator_type, locator, driver=WebDriver.web_driver, name=name, parent=parent)


class WebElement(BaseElement):
    def __init__(self, locator_type, locator, name=None, parent=None):
        self.driver = WebDriver.web_driver
        super().__init__(locator_type, locator,
                         driver=WebDriver.web_driver, config=ConfigManager(), name=name,
                         parent=parent)
        self.ALLOWED_DYNAMIC_METHODS = ["click", "text"]

    def assert_element_placeholder(self, expected):
        """
        assert that element placeholder is equal to expected
        """
        element_placeholder = self.element.get_attribute("placeholder")
        assert_should_be_equal(actual_value=element_placeholder, expected_value=expected, silent=True)

    def assert_element_active(self, should_active=True):
        """
        assert that element class contain active attribute
        """
        actual = self.is_element_active()
        assert_should_be_equal(actual_value=actual, expected_value=should_active,
                               message=f"Verify is element {self.element.name} active")

    def is_element_active(self):
        element_class = self.element.get_attribute("class")
        if "active" in element_class:
            return True
        return False

    def scroll_to_element(self):
        actions = ActionChains(self.driver)
        actions.move_to_element(self.element()).perform()

    def click_with_js(self):
        WebDriver.web_driver.execute_script("arguments[0].click()", self.element())


class WebTextBox(TextBoxActionsMixin, WebElement):
    pass
