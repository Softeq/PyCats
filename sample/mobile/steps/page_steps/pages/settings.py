from common._webdriver_qa_api.core.utils import fail_test
from common.facade import logger
from sample.mobile.src.pages.settings_page import SettingsPage


class SettingsSteps(SettingsPage):

    def select_unit(self, temperature_format: str):
        """ Select temperature format
        :param temperature_format: format shortcut as string 'c' - Celsius, 'f' - fahrenheit
        """
        logger.log_info(f"Choose '{temperature_format}' temperature unit")
        if temperature_format.lower() == 'c':
            self.select_celsius_unit()
        elif temperature_format.lower() == 'f':
            self.select_fahrenheit_unit()
        else:
            fail_test(f"Unknown temperature temperature_format - '{temperature_format}'")
