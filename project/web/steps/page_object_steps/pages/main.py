from project.web.pages.main_page import MainPage
from common.facade import logger


class MainPageSteps(MainPage):

    def search_city(self, city, select_city=False):
        logger.log_title(f"Search city by name: '{city}'")
        self.fill_city_to_search(city)
        self.click_search()

        if select_city is True:
            logger.log_title(f"Select city by name: '{city}'")
            self.city_dropdown.select_by_text(city)
