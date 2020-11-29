from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class SetupNotificationPage(MobilePage):

    def __init__(self, should_present=True):
        super().__init__(locator_type=By.ID,
                         locator='com.yahoo.mobile.client.android.weather:id/onboarding_notifications_fragment_holder',
                         name="Notification Start page", should_present=should_present)

        self.lbl_title = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/onboarding_title_text")
        self.lbl_description = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                    "onboarding_subtitle_text")
        self.chb_daily_notification = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                           "onboarding_notification_daily_weather_check_text")
        self.chb_precipitation_notification = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                                   "onboarding_notification_near_term_"
                                                                   "precipitation_check_text")
        self.chb_temperature_notification = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                                 "onboarding_notification_temperature_change_check_text")
        self.chb_severe_notification = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                            "onboarding_notification_severe_weather_check_text")
        self.btn_enable = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                               "onboarding_notifications_positive_button")
        self.btn_decline = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/"
                                                "onboarding_notifications_negative_button")

    def click_enable(self):
        self.btn_enable.click()

    def click_decline(self):
        self.btn_decline.click()
