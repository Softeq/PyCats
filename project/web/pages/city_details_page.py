import re

from common._webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement


class CityDetailsContainer(WebPage):

    def __init__(self):
        super().__init__(By.XPATH, "//div[@class='current-container mobile-padding']", "City Details Container")
        container_element = WebElement(By.XPATH, "//div[@class='current-container mobile-padding']")
        self.lbl_temperature = WebElement(By.XPATH, "div[2]/div[1]/span", parent=container_element)
        self.lbl_pressure = WebElement(By.XPATH, "//li[./*[@class='icon-pressure']]", parent=container_element)
        self.lbl_humidity = WebElement(By.XPATH, "//li[./span[text()='Humidity:']]", parent=container_element)
        self.lbl_city = WebElement(By.XPATH, "div/h2", parent=container_element)

    def get_pressure_value(self):
        return self.lbl_pressure.get_element_text()[:-3]

    def get_humidity_value(self):
        return self.lbl_humidity.get_element_text().split()[1][:-1]

    def get_temperature_value(self):
        temperature_value = self.lbl_temperature.get_element_text()
        return re.findall(r'\d+', temperature_value)[0]
