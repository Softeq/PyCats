from common._webdriver_qa_api.core.utils import fail_test
from project.mobile.src.pages.settings_page import SettingsPage


class SettingsSteps(SettingsPage):

    def select_unit(self, temperature_formate: str):
        """ Select temperature format
        :param temperature_formate: format shortcut as string 'c' - Celsius, 'f' - fahrenheit
        """
        if temperature_formate.lower() == 'c':
            self.select_celsius_unit()
        elif temperature_formate.lower() == 'f':
            self.select_fahrenheit_unit()
        else:
            fail_test(f"Unknown temperature temperature_format - '{temperature_formate}'")
