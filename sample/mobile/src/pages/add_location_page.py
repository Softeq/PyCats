from common._webdriver_qa_api.core.utils import fail_test
from common._webdriver_qa_api.mobile.mobile_element import MobileElement, MobileTextBox, MobileElements
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class AddLocationPage(MobilePage):

    def __init__(self):
        super().__init__(locator_type=By.ID,
                         locator='com.yahoo.mobile.client.android.weather:id/list',
                         name="Add location page")
        self.txb_search_location = MobileTextBox(By.ID, "location_search_box")
        self.btn_clear = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/close_button")

        self.view_search_result = MobileElement(By.ID, "location_search_result")
        self.lbl_location_name = MobileElements(By.ID, "location_name")

    def _is_results_present(self):
        return self.view_search_result.try_wait_element(timeout=5)

    def set_location_name(self, value):
        return self.txb_search_location.set_text(value)

    def click_clear(self):
        self.btn_clear.click()

    def click_result_by_text(self, value):
        if not self._is_results_present():
            fail_test("Can't select city {}, result list not present")

        for city in self.lbl_location_name.get_elements():
            if value in city.text:
                city.click()
                break

    def verify_value_in_result(self, value):
        if not self._is_results_present():
            fail_test("Can't select city {}, result list not present")

        results_list = self.lbl_location_name.get_elements_text()
        for location_name in results_list:
            if value in location_name:
                return
        fail_test("There is no {} in result table".format(value))
