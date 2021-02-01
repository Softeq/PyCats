from common.facade import logger
from project.web.pages.home_page import HomePage


class HomePageSteps(HomePage):

    def get_api_key(self):
        logger.log_title("Get REST API key")
        self.click_api_keys_menu()
        return self.lbl_api_key.text
