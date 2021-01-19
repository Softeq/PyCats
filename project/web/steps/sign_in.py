from project.web.pages.sign_in_page import SignInPage
from project.test_data.users import User


class SignInSteps(SignInPage):

    def login(self, email: str, password: str):
        self.fill_email(email)
        self.fill_password(password)
        self.click_submit_btn()

    def verify_error_text(self, expected=None):
        if expected is None:
            self.lbl_error.assert_present(is_present=False, timeout=3)
        else:
            self.lbl_error.assert_present(timeout=3)
            self.lbl_error.assert_element_text(expected=expected)

    def test_changes(self):
        self.lbl_error.is_present_without_waiting()
