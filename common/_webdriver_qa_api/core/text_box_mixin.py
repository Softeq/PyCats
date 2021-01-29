import logging
from typing import Optional, Union, Dict
from selenium.webdriver.common.keys import Keys
from common._webdriver_qa_api.core.utils import assert_should_be_equal

logger = logging.getLogger(__name__)


class TextBoxActionsMixin:

    def set_text(self, text: Optional[str], skip_if_none: bool = True, blur_and_focus: bool = False):
        """
        clear the text field and type new text
        :param text: text that should be set
        :param skip_if_none: true - do nothing if text isn't specified, set text if it specified
        false - set text if it specified, error if text isn't specified
        :param blur_and_focus: true - reset focus to element field
        """
        if text is None and skip_if_none:
            return self
        logger.info(f"Clear text field '{self.element.name}' and set text '{text}'")
        self.element.clear()
        self.element.send_keys(text)
        if blur_and_focus:
            self.blur_and_focus()

    def type_text(self, text: str):
        """
        type text into the text field
        :param text: text that should be typed
        """
        logger.info(f"Type text '{text}' into text field '{self.element.name}'")
        self.element.send_keys(text)

    def clear_text(self):
        """
        clear text in the text field
        """
        logger.info(f"Clear text in the field '{self.element.name}")
        self.element.clear()

    def assert_is_text_masked(self, is_masked: bool = True):
        """
        assert element text masked, test fails if expected state isn't equal to actual
        :param is_masked: if true - should be masked, if false - not masked
        """
        # @todo: check on masked field, not sure that it will work for any case
        expected_state = "true" if is_masked else "false"
        actual_state = self.element.get_attribute("password")
        assert_should_be_equal(actual_value=actual_state, expected_value=expected_state,
                               message="Verify is '{0}' field {1}masked".format(
                                   self.element.name, '' if is_masked else 'not '))

    def blur_and_focus(self):
        """ Reset focus to target element """
        self.element.click()
        self.element.send_keys(Keys.TAB)
        self.element.click()

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return self.element.get_attribute('value')
