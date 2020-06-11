from project.web.pages.sign_in_page import SignInPage
from project.test_data.users import User


class SignInSteps(SignInPage):

    def login(self, user_obj: User):
        self.fill_email(user_obj.email)
        self.fill_password(user_obj.password)
        self.click_submit_btn()
