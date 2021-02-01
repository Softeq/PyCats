import time
import logging
from typing import Union

from common._webdriver_qa_api.core.utils import assert_should_be_equal
from common._webdriver_qa_api.core.base_elements import BaseElement

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver, config, locator_type=None, locator=None,
                 name=None):
        self.driver = driver
        self.locator_type = locator_type
        self.locator = locator
        self.name = locator if name is None else name
        self._config = config

    def assert_page_present(self, second: Union[int, float] = 20):
        """
        assert page present, test fails if page is absent
        """
        assert_should_be_equal(actual_value=self.is_page_present(second=second), expected_value=True,
                               message=f"Verify is page '{self.name}' opens in {second} seconds")
        logger.info(f"Page '{self.name}' is opened")

    def assert_page_not_present(self, second: Union[int, float] = 20):
        """
        assert page not present, test fails if page is present
        """
        assert_should_be_equal(actual_value=self.is_page_present(second=second), expected_value=False,
                               message=f"Verify is page '{self.name}' absent in {second} seconds")

    def is_page_present(self, second: Union[int, float] = 0.1) -> bool:
        """
        Get page initial element and return True if element present
        """
        logger.info(f"Check is page '{self.name}' present in {second} seconds")
        end_time = time.time() + second
        present_status = False
        while time.time() < end_time and not present_status:
            present_status = BaseElement(self.locator_type,
                                         self.locator,
                                         self.driver,
                                         self._config,
                                         self.name).is_present_without_waiting()
            time.sleep(0.1)
        return present_status

    def refresh_page(self):
        """
        refresh current page
        """
        logger.info("Refresh current page")
        self.driver.refresh()
        self.assert_page_present()

    def navigate_to(self, url: str):
        logger.info(f"Going to {url}")
        self.driver.get(url)
