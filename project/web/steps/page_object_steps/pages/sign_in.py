from common.facade import logger
from project.web.pages.sign_in_page import SignInPage


class SignInSteps(SignInPage):

    def login(self, email: str, password: str):
        logger.log_title(f"Login to account using credentials: {email} / {password}")
        self.fill_email(email)
        self.fill_password(password)
        self.click_submit_btn()

    def verify_login_error(self, expected=None):
        logger.log_title(f"Verify error is {'not' if not expected else ''} displayed on the page")
        if expected is None:
            self.lbl_error.assert_present(is_present=False, timeout=3)
        else:
            self.lbl_error.assert_present(timeout=3)
            self.lbl_error.assert_element_text(expected=expected)

    def verify_default_elements(self):
        logger.log_title(f"Verify default elements state on {self.name}")
        self.lbl_form_title.assert_visible(timeout=5)
        self.lbl_form_title.assert_element_text("Sign In To Your Account")

        self.txb_email.assert_visible()
        self.txb_email.assert_element_placeholder(expected="Enter email")
        self.txb_email.assert_element_text_empty()

        self.txb_password.assert_visible()
        self.txb_password.assert_element_placeholder(expected="Password")
        self.txb_password.assert_element_text_empty()

        self.btn_submit.assert_visible()
        self.btn_submit.assert_enabled()

        self.btn_create_account.assert_visible()
        self.btn_create_account.assert_enabled()

        self.btn_recover.assert_visible()
        self.btn_recover.assert_enabled()
