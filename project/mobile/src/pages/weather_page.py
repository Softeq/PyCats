from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class WeatherPage(MobilePage):

    def __init__(self):
        super().__init__(locator_type=By.ID,
                         locator='weather',
                         name="Main weather page")
        self.lbl_location = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/location")
        self.lbl_location_time = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/local_time")

        self.btn_menu = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/sidebarButton")
        self.btn_add_location = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/addLocationButton")

        self.lbl_current_temperature = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/temperature")
        self.lbl_weather_description = MobileElement(By.ID, "weather_description")
        self.lbl_max_daily_temperature = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/temp_high")
        self.lbl_min_daily_temperature = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/temp_low")

        self.img_refresh = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/fl_inner")

    def refresh_data(self):
        self.swipe_down()
        self.img_refresh.wait_element_absent(second=5)

    def get_location(self) -> str:
        return self.lbl_location.text

    def get_current_temperature(self) -> int:
        return int(self.lbl_current_temperature.text[:-1])

    def get_high_temperature(self) -> int:
        return int(self.lbl_max_daily_temperature.text[:-1], self.lbl_min_daily_temperature.text[:-1])

    def click_add_location(self):
        self.btn_add_location.click()

    def open_menu(self):
        self.btn_menu.click()
