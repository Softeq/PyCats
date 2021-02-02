import pytest

from common.facade import logger
from project import web
from project.test_data.users import valid_user
from project.web.pages.reset_password_form import ResetPasswordForm


@pytest.mark.usefixtures('open_main_page')
class TestSignIn:
    """ Weather - sign in to account tests """

    users = [
        pytest.param(valid_user.email, valid_user.password, None, id="valid_user"),
        pytest.param('invalid_user', valid_user.password, "Invalid Email or password.", id="invalid_user"),
        pytest.param('', '', "Invalid Email or password.", id="not_filled"),
        pytest.param(valid_user.email, '', "Invalid Email or password.", id="password_not_filled"),
        pytest.param('', valid_user.password, "Invalid Email or password.", id="email_not_filled"),
        pytest.param('', valid_user.password, "", id="email_not_filled")
    ]

    def test_sign_in_page_displayed(self):
        """ Recover account button transaction """
        logger.log_step("Open sign in page", precondition=True)
        sign_in_page = web.navigation_steps.navigate_to_sign_in_page()

        logger.log_step("Verify default elements on the page")
        sign_in_page.verify_default_elements()

    @pytest.mark.parametrize("email, password, error", users)
    def test_login(self, email, password, error):
        """ Login to account test """
        logger.log_step("Open sign in page", precondition=True)
        sign_in_page = web.navigation_steps.navigate_to_sign_in_page()

        logger.log_step("Login to account")
        sign_in_page.login(email, password)

        logger.log_step("Verify login result")
        sign_in_page.verify_login_error(expected=error)

    def test_create_account_transaction(self):
        """ Create account button transaction """
        logger.log_step("Open sign in page", precondition=True)
        sign_in_page = web.navigation_steps.navigate_to_sign_in_page()

        logger.log_step("Verify create_account button transaction")
        sign_in_page.click_create_account()
        web.pages.SignUpSteps()

    def test_reset_password_transaction(self):
        """ Recover account button transaction """
        logger.log_step("Open sign in page", precondition=True)
        sign_in_page = web.navigation_steps.navigate_to_sign_in_page()

        logger.log_step("Verify recovery password button transaction")
        sign_in_page.click_recover_password()
        ResetPasswordForm()
