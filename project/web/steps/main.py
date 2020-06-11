from project.web.pages.main_page import MainPage


class MainPageSteps(MainPage):

    def search_city(self, city):
        self.fill_city_to_search(city)
        self.click_search()

    def click_login(self):
        self.click_sign_in()
