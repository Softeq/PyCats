from common.facade import logger
from project.web.pages.sign_in_page import SignInPage


class SignInSteps(SignInPage):

    def login(self, email: str, password: str):
        logger.log_title(f"Login to account using credentials: {email} / {password}")
        self.fill_email(email)
        self.fill_password(password)
        self.click_submit_btn()

    def verify_error_text(self, expected=None):
        logger.log_title(f"Verify error is {'not' if not expected else ''} displayed on the page")
        if expected is None:
            self.lbl_error.assert_present(is_present=False, timeout=3)
        else:
            self.lbl_error.assert_present(timeout=3)
            self.lbl_error.assert_element_text(expected=expected)
