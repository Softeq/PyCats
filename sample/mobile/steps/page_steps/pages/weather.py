from common._webdriver_qa_api.core.utils import assert_should_be_equal
from sample.mobile.src.pages.weather_page import WeatherPage


class WeatherSteps(WeatherPage):

    def verify_selected_city(self, value):
        assert_should_be_equal(actual_value=self.get_location(), expected_value=value,
                               message="Verify selected location.")

    def verify_current_temperature(self, value):
        self.refresh_data()
        assert_should_be_equal(actual_value=self.get_current_temperature(), expected_value=value,
                               message="Verify current temperature location.")

    def sample_to_check_format(self):
        self.btn_menu.get_element_size()
