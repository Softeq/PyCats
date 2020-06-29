import logging

from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)


class TextBoxActionsMixin:

    def set_text(self, text, skip_if_none=True, blur_and_focus=False):
        """
        clear the text field and type new text
        :param text: text that should be set
        :param skip_if_none: true - do nothing if text isn't specified, set text if it specified
        false - set text if it specified, error if text isn't specified
        """
        if text is None and skip_if_none:
            return self
        logger.info(f"Clear text field '{self.element.name}' and set text '{text}'")
        self.element.clear()
        self.element.send_keys(text)
        if blur_and_focus:
            self.blur_and_focus()
        return self

    def type_text(self, text, force_open_keyboard=False):
        """
        type text into the text field
        :param text: text that should be typed
        :param force_open_keyboard: if True tap the field to open keyboard
        """
        logger.info(f"Type text '{text}' into text field '{self.element.name}'")
        if force_open_keyboard:
            self.element.click()
        self.element.send_keys(text)
        return self

    def clear_text(self):
        """
        clear text in the text field
        """
        self.element.clear()
        return self

    def assert_is_text_masked(self, is_masked=True):
        """
        assert element text masked, test fails if expected state isn't equal to actual
        :param is_masked: if true - should be masked, if false - not masked
        """
        if is_masked:
            expected_state = "true"
        else:
            expected_state = "false"
        actual_state = self.element.get_attribute("password")
        if actual_state == expected_state:
            logger.info("Correct state of '{0}': masked={1}".format(
                self.element.name, actual_state))
        else:
            logger.log_fail(
                "Incorrect state of '{0}': masked={1}. Expected state: masked={2}".format(
                    self.element.name, actual_state, expected_state))
        assert (actual_state == expected_state)

    def blur_and_focus(self):
        self.element.click()
        self.element.send_keys(Keys.TAB)
        self.element.click()

    @property
    def value(self):
        return self.element.get_attribute('value')
