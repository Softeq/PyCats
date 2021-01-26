from project.web.pages.main_page import MainPage
from common.facade import logger


class MainPageSteps(MainPage):

    def search_city(self, city):
        logger.log_title(f"Search city by name: '{city}'")
        self.fill_city_to_search(city)
        self.click_search()
