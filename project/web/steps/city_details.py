from project.web.pages.city_details_page import CityDetailsPage


class CityDetailsSteps(CityDetailsPage):

    def get_weather_info(self):
        self.widget_temperature.wait_element()
        weather_info = {"pressure": self.lbl_pressure.text.split()[0],
                        "humidity": self.lbl_humidity.text.split()[0],
                        "sunrise": self.lbl_sunrise.text,
                        "sunset": self.lbl_sunset.text,
                        }
        return weather_info
