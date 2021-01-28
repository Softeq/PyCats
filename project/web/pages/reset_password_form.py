import time
from typing import Union

from selenium.webdriver.common.by import By

from common._webdriver_qa_api.core.base_elements import BaseElement
from common._webdriver_qa_api.web.web_elements import WebElement, WebTextBox
from common.facade import logger
from .sign_in_page import SignInPage


class ResetPasswordForm(SignInPage):

    def __init__(self, should_present=True):
        super().__init__(should_present=False)
        self.locator_type = By.XPATH
        self.locator = "//form[@action='/users/password']"
        self.name = "Reset password Form"

        self.lbl_form_title = WebElement(By.XPATH, "//div[@class='sign-form']/h3")
        self.txb_username = WebTextBox(By.XPATH, self.locator + "//input[@id='user_username']")
        self.btn_submit = WebTextBox(By.ID, self.locator + "//input[@type='submit']")
        if should_present:
            self.assert_page_present(30)

    def is_page_present(self, second: Union[int, float] = 0.1) -> bool:
        """
        Get page initial element and return True if element present
        """
        logger.info(f"Check is page '{self.name}' present in {second} seconds")
        end_time = time.time() + second
        present_status = False
        try:
            while time.time() < end_time and not present_status:
                self.driver.implicitly_wait(1)
                present_status = BaseElement(self.locator_type, self.locator,
                                             self.driver, self._config, self.name).is_displayed()
                time.sleep(0.1)
        finally:
            self.driver.implicitly_wait(self._config.get_webdriver_settings().webdriver_implicit_wait_time)
        return present_status
