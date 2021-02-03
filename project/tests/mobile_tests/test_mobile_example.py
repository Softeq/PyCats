import pytest

from common.facade import logger
from project import mobile


@pytest.mark.usefixtures("start_mobile_session")
@pytest.mark.C00001
def test_mobile_temperature_unit_switch():
    """
    Test to check switching of temperature unit

    Steps:
    1. Open Weather app and navigate to main page
    2. Set Celsius unit in settings screen
    3. Get current temperature on main screen
    4. Set Fahrenheit unit in settings screen
    5. Get current temperature on main screen and compare with celsius value
    """
    logger.log_step("Set Celsius unit in settings screen")
    dashboard_page = mobile.navigation_steps.navigate_to_main_page()
    dashboard_page.open_menu()

    menu = mobile.pages.NavigationMenuSteps()
    menu.click_settings()

    settings_page = mobile.pages.SettingsSteps()
    settings_page.select_celsius_unit()
    settings_page.click_back()

    logger.log_step("Get current temperature in celsius format")
    dashboard_page.assert_page_present()
    celsius_value = dashboard_page.get_current_temperature()

    logger.log_step("Set Fahrenheit unit on settings screen")
    dashboard_page.open_menu()
    menu.assert_page_present()
    menu.click_settings()

    settings_page.assert_page_present()
    settings_page.select_fahrenheit_unit()
    settings_page.click_back()

    logger.log_step("Get current temperature in fahrenheit and compare with celsius value")
    dashboard_page.assert_page_present()
    dashboard_page.verify_current_temperature(value=int((celsius_value * 9 / 5) + 32))
