from common._webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement, WebTextBox
from sample.web.custom_elements.search_dropdown_menu import SearchDropDownMenu


class MainPage(WebPage):

    def __init__(self):
        super().__init__(By.XPATH, '//div[@class="section main-section"]', "Weather main page")
        self.txb_search = WebTextBox(By.XPATH, "//input[@placeholder='Search city']")
        self.btn_search = WebElement(By.XPATH, "//button[@type='submit']")
        self.btn_sign_in = WebElement(By.XPATH, "//a[contains(@href, '/home/sign_in')]")
        self.city_dropdown = SearchDropDownMenu(menu_element=WebElement(By.CLASS_NAME, "search-dropdown-menu"),
                                                item_xpath_locator="li/span[1]")

    def fill_city_to_search(self, city):
        self.txb_search.set_text(city)

    def click_search(self):
        self.btn_search.wait_element_enabled()
        self.btn_search.click()

    def click_sign_in(self):
        self.btn_sign_in.wait_element_enabled()
        self.btn_sign_in.click()
