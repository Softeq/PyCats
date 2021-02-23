from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.switch import MobileSwitch
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class SettingsPage(MobilePage):

    def __init__(self):
        super().__init__(locator_type=By.ID,
                         locator='com.yahoo.mobile.client.android.weather:id/settings_scroll',
                         name="Settings page")
        self.btn_back = MobileElement(By.XPATH, "//android.widget.ImageButton[@content-desc='Navigate up']")
        self.lbl_unit = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/units_text")
        self.chb_c_unit = MobileSwitch(By.ID, "com.yahoo.mobile.client.android.weather:id/settings_c_toggle")
        self.chb_f_unit = MobileSwitch(By.ID, "com.yahoo.mobile.client.android.weather:id/settings_f_toggle")

    def click_back(self):
        self.btn_back.click()

    def select_celsius_unit(self):
        self.chb_c_unit.set_switcher_state(checked=True)

    def select_fahrenheit_unit(self):
        self.chb_f_unit.set_switcher_state(checked=True)
