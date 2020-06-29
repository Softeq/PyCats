from common._webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement


class HomePage(WebPage):

    def __init__(self):
        super().__init__(By.ID, "myTab", "Account Home Page")
        self.lnk_api_keys = WebElement(By.XPATH, "//li/a[@href='/api_keys']")
        self.lbl_api_key = WebElement(By.XPATH, "//table//pre")

    def click_api_keys_menu(self):
        self.lnk_api_keys.click()
