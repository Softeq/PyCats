from common.facade import logger
from sample.web.pages.city_details_page import CityDetailsContainer


class CityDetailsSteps(CityDetailsContainer):

    def get_weather_info(self):
        logger.log_title("Get current weather info from city page")
        self.lbl_temperature.wait_element()
        weather_info = {"pressure": self.get_pressure_value(),
                        "humidity": self.get_humidity_value(),
                        "temperature": self.get_temperature_value()
                        }
        return weather_info

    def verify_selected_city(self, city, timeout=5):
        logger.log_title(f"Verify selected city is '{city}'")
        self.lbl_city.assert_element_contains_text(expected=city, timeout=timeout)
