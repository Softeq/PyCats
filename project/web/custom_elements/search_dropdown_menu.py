from selenium.webdriver.common.by import By

from common._webdriver_qa_api.core.utils import fail_test
from common._webdriver_qa_api.web.web_elements import WebElement, WebElements


class SearchDropDownMenu:

    def __init__(self, menu_element: WebElement, item_xpath_locator: str, name=None):
        self._menu_item = menu_element
        self._item_path = item_xpath_locator
        self.name = name if name else menu_element.name

    @property
    def menu(self) -> WebElement:
        return self._menu_item

    @property
    def menu_items(self) -> WebElements:
        return WebElements(By.XPATH, self._item_path, parent=self.menu)

    def select_by_index(self, index: int):
        self.menu_items.elements()[index].click()

    def select_by_text(self, text: str):
        for element in self.menu_items.elements():
            if text in element.text:
                element.click()
                return
        fail_test(KeyError(f"There is no item '{text}' in the dropdown list"))
