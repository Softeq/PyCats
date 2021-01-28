from typing import List
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement


class DropDownMixin:

    @property
    def menu(self) -> WebElement:
        return WebElement(By.CSS_SELECTOR, "div[aria-hidden='false']")

    @property
    def menu_items(self) -> List['WebElement']:
        return self.menu.element().find_elements(By.CLASS_NAME, 'dropdown-item')

    def open_menu(self):
        self.click()
        self.menu.wait_element_visible()

    def select_by_index(self, index: int):
        self.menu_items[index].click()

    def select_by_text(self, text: str):
        for element in self.menu_items:
            if element.text == text:
                element.click()
                return
        raise KeyError(f"There is no item '{text}' in the dropdown list")

    def select_by_value(self, value):
        for element in self.menu_items:
            if element.get_attribute('value') == value:
                element.click()
                return
        raise KeyError(f"There is no item '{value}' in the dropdown list")
