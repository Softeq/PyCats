from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class SetupLocationPage(MobilePage):

    def __init__(self, should_present=True):
        super().__init__(locator_type=By.ID,
                         locator='onboarding_setup_locations_fragment_holder',
                         name="Setup location page", should_present=should_present)
        self.lbl_title = MobileElement(By.ID, "onboarding_location_setup_title_text")
        self.lbl_description = MobileElement(By.ID, "onboarding_location_setup_subtitle_text")

        self.btn_continue = MobileElement(By.ID, "onboarding_location_setup_positive_button")

    def click_continue(self):
        self.btn_continue.click()
