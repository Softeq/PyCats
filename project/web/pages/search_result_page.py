from common.webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common.webdriver_qa_api.web.web_elements import WebElement


class SearchResult(WebPage):

    def __init__(self):
        super().__init__(By.XPATH, "//h2[text()='Weather in your city']", "Search Result page")
        self.lnk_search_result_row = WebElement(By.XPATH, "//table//a")

    def click_first_result(self):
        self.lnk_search_result_row.wait_element()
        self.lnk_search_result_row.click()
