from common.webdriver_qa_api.core.base_pages import BasePage
from common.webdriver_qa_api.web.web_driver import WebDriver


class WebPage(BasePage):
    def __init__(self, locator_type=None, locator=None, name=None, should_present=True):
        super().__init__(driver=WebDriver.web_driver, name=name, locator_type=locator_type, locator=locator)
        if should_present and not (locator_type and locator):
            raise ValueError("locator_type and locator arguments are required for should_present=True")
        elif should_present:
            self.assert_page_present(30)
