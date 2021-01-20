from typing import Optional
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from common.config_manager import ConfigManager
from common._webdriver_qa_api.web.web_driver import get_webdriver_session
from common._webdriver_qa_api.core.utils import assert_should_be_equal
from common._webdriver_qa_api.core.base_elements import BaseElement, BaseElements
from common._webdriver_qa_api.core.text_box_mixin import TextBoxActionsMixin


class WebElements(BaseElements):
    def __init__(self, locator_type: str, locator: str, name: str = None, parent: BaseElement = None):
        super().__init__(locator_type, locator, driver=get_webdriver_session().driver, name=name, parent=parent)


class WebElement(BaseElement):
    def __init__(self, locator_type: str, locator: str, name: str = None,
                 parent: Optional[BaseElement] = None, frame: Optional[BaseElement] = None):
        self.driver = get_webdriver_session().driver
        self.frame = frame
        super().__init__(locator_type, locator,
                         driver=self.driver, config=ConfigManager(), name=name,
                         parent=parent)
        self.ALLOWED_DYNAMIC_METHODS = ["click", "text"]

    def __getattribute__(self, item):
        if item == 'element':
            if self.frame is not None:
                frame_element = self.frame.element.selenium_element
                self.driver.switch_to.frame(frame_element)
            else:
                self.driver.switch_to.default_content()
        return super(WebElement, self).__getattribute__(item)

    def assert_element_placeholder(self, expected: str):
        """
        assert that element placeholder is equal to expected
        """
        element_placeholder = self.element.get_attribute("placeholder")
        assert_should_be_equal(actual_value=element_placeholder, expected_value=expected, silent=True)

    def assert_element_active(self, should_active: bool = True):
        """
        assert that element class contain active attribute
        """
        actual = self.is_element_active()
        assert_should_be_equal(actual_value=actual, expected_value=should_active,
                               message=f"Verify is element {self.element.name} active")

    def is_element_active(self) -> bool:
        return "active" in self.element.get_attribute("class")

    def scroll_to_element(self):
        actions = ActionChains(self.driver)
        actions.move_to_element(self.element()).perform()

    def click_with_js(self):
        self.driver.execute_script("arguments[0].click()", self.element())


class WebTextBox(TextBoxActionsMixin, WebElement):

    def set_text(self, text, skip_if_none=True, blur_and_focus=False):
        """
        clear the text field and type new text
        :param text: text that should be set
        :param skip_if_none: true - do nothing if text isn't specified, set text if it specified
        false - set text if it specified, error if text isn't specified
        """
        super(WebTextBox, self).set_text(text=text, skip_if_none=skip_if_none)
        if blur_and_focus:
            self.blur_and_focus()
        return self

    def blur_and_focus(self):
        self.element.click()
        self.element.send_keys(Keys.TAB)
        self.element.click()
