from project.web.pages.home_page import HomePage


class HomePageSteps(HomePage):

    def get_api_key(self):
        self.click_api_keys_menu()
        return self.lbl_api_key.text
