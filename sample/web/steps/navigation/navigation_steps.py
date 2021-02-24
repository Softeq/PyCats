from common._webdriver_qa_api.web.web_driver import navigate_to
from common.facade import logger, raw_config
from sample import web

__all__ = ['navigate_to_sign_in_page']


def navigate_to_sign_in_page():
    logger.log_title(f"Navigate to Sign in page")
    navigate_to(raw_config.project_settings.web_app_url)

    main_steps = web.pages.MainPageSteps()
    main_steps.click_sign_in()
    return web.pages.SignInSteps()
