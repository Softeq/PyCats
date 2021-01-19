import pytest

from common.facade import logger
from project.web.steps.main import MainPageSteps
from project.web.steps.sign_in import SignInSteps
from project.test_data.users import valid_user

users = [
    pytest.param(valid_user.email, valid_user.password, None, id="valid_user"),
    pytest.param('invalid_user', valid_user.password, "Invalid Email or password.", id="invalid_user"),
]


@pytest.mark.parametrize("email, password, error", users)
@pytest.mark.usefixtures('open_main_page')
def test_login(email, password, error):
    logger.log_step(f"Open Main Page and navigate to sign in page")
    main_steps = MainPageSteps()
    main_steps.click_login()

    logger.log_step("Click on the first search result")
    sign_in_page = SignInSteps()
    sign_in_page.login(email, password)

    logger.log_step("Verify login result")
    sign_in_page.test_changes()
    sign_in_page.verify_error_text(expected=error)
