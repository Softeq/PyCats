from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class NavigationMenuPage(MobilePage):

    def __init__(self):
        super().__init__(locator_type=By.ID,
                         locator='com.yahoo.mobile.client.android.weather:id/sidebar_menu',
                         name="Navigation menu page")
        self.btn_sign_in = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/account_sign_in")
        self.btn_edit_location = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/menu_edit_location")
        self.btn_current_location = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                         "menu_location_item")
        self.btn_settings = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/sidebar_item_settings")
        self.btn_feedback = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                 "sidebar_item_send_feedback")
        self.btn_share = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                              "sidebar_item_share_this_app_custom")
        self.btn_rate = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/sidebar_item_rate_this_app")
        self.img_logo = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/sidebar_logo")
        self.btn_tos = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/sidebar_privacy")

    def click_sign_in(self):
        self.btn_sign_in.click()

    def click_settings(self):
        self.btn_settings.click()
