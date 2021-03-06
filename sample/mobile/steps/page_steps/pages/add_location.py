from common.facade import logger
from sample.mobile.src.pages.add_location_page import AddLocationPage


class AddLocationSteps(AddLocationPage):

    def select_location_by_value(self, value):
        logger.log_title(f'Select location {value} on search page')
        if self._is_results_present():
            self.click_clear()

        self.set_location_name(value)
        self.click_result_by_text(value)
