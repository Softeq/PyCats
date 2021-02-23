# project - Mobile app

This section contains sample of mobile app tests based on UI interface interactions.

## Code structure

We support 3 layers structure for code base:

* Builder layer - implementation of Page Object pattern: include page elements and actions on the page
* Steps layer - steps functions with UI actions and checks
* Tests layer - tests scenarios 


## Development practices:

### Builder layer
 Implementation of Page object pattern based on Page modules (For each mobile screen we have separate class).
 Each page module contains implementation of screen for both platforms and command base class with abstract methods for this screen.
 This layer describes mobile screens and actions that we can do on them.
 
 That layer placed in `src` directory and divided by following object types: 
 
 * [confirmations popups](src/confirmations)
 * [screens](src/pages)
 
 
The Page object implementation should include following rules:

1. The screen modules should contains Page object implementation class, in format: {screen_name}Page, e.g. `LoginPage`
1. The page classes must inherit from [MobilePage](../../common/_webdriver_qa_api/mobile/mobile_page.py) class and implement `super` call for __init__ method
1. All page elements should be defined in __init__ method as [MobileElement](../../common/_webdriver_qa_api/mobile/mobile_element.py) related objects (from common elements types in framework part or [custom elements](src/custom_elements) types in project part)
1. All elements variable names starts with element type shortcut: button - `self.btn_name`, text_box - `self.txb_name` etc


sample of Page module:
```python
from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.switch import MobileSwitch
from common._webdriver_qa_api.mobile.mobile_page import MobilePage
from selenium.webdriver.common.by import By


class SettingsPage(MobilePage):

    def __init__(self):
        super().__init__(locator_type=By.ID,
                         locator='com.yahoo.mobile.client.android.weather:id/settings_scroll',
                         name="Settings page")
        self.btn_back = MobileElement(By.XPATH, "//android.widget.ImageButton[@content-desc='Navigate up']")
        self.lbl_unit = MobileElement(By.ID, "com.yahoo.mobile.client.android.weather:id/units_text")
        self.chb_c_unit = MobileSwitch(By.ID, "com.yahoo.mobile.client.android.weather:id/settings_c_toggle")
        self.chb_f_unit = MobileSwitch(By.ID, "com.yahoo.mobile.client.android.weather:id/settings_f_toggle")

    def click_back(self):
        self.btn_back.click()

    def select_celsius_unit(self):
        self.chb_c_unit.set_switcher_state(checked=True)

    def select_fahrenheit_unit(self):
        self.chb_f_unit.set_switcher_state(checked=True)
```

### Steps layer
Steps layer - it's a function set that combines Action methods from Builder layer and expands them with test checks.
This solution helps us to have a clear structure of tests and avoid code duplication (save time on test supporting)

That layer placed in `steps` directory, and divided to 2 main parts:

* [Navigation steps](steps/navigation_steps/navigation_steps.py) - function that used for navigation between mobile screens
* [Global steps](steps/global_steps/global_steps.py) - functions that combine many actions for frequent uses (like login)
* [Screen steps](steps/page_steps/pages) - functions that combine actions and checks for a specific page of the application


The `navigation` keywords should include following rules:

1. Navigation function combine actions from: another steps, PO classes, checks
1. Should return an object of Page class
1. Have a log_title message with action message
1. Function should be added to __all__ module list 

sample of navigation method:
```python
__all__ = ['navigate_to_main_page']

from common.facade import logger

from sample.mobile.src.confirmations.location_permission import LocationPermissionAndroid
from sample.mobile.steps.page_steps.pages.setup_notification import SetupNotificationSteps
from sample.mobile.steps.page_steps.pages.setup_location import SetupLocationSteps
from sample.mobile.steps.page_steps.pages.weather import WeatherSteps


def navigate_to_main_page():
    logger.log_title("Navigate to main Weather Page")

    location_permission = LocationPermissionAndroid(should_present=False)
    if location_permission.is_page_present(second=2):
        location_permission.deny()

    setup_notification_page = SetupNotificationSteps(should_present=False)
    if setup_notification_page.is_page_present(second=2):
        setup_notification_page.click_decline()

    setup_location_page = SetupLocationSteps(should_present=False)
    if setup_location_page.is_page_present(second=2):
        setup_location_page.click_continue()

    return WeatherSteps()
```


The `Global steps` keywords should include following rules:

1. Function combine actions from: another steps, steps classes, checks
1. Have a log_title call with action message
1. Function should be added to __all__ module list

sample of steps method:
```python
__all__ = ['add_location']

from common.facade import logger
from sample.mobile.steps.page_steps.pages.weather import WeatherSteps
from sample.mobile.steps.page_steps.pages.add_location import AddLocationSteps


def add_location(city):
    logger.log_title(f"Add '{city}' to location list")
    weather_steps = WeatherSteps()
    weather_steps.click_add_location()

    add_location_page = AddLocationSteps()
    add_location_page.select_location_by_value(value=city)
    return WeatherSteps()
```


The `Page steps` keywords should include following rules:

1. The Steps class should inherit from PO class for same screen
1. Class function combine actions from: Page classes, Steps classes and checks
1. Have a log_info or log_title call with step message
1. Function should be added to __all__ module list


sample of page steps class:
```python
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
```

#### Test layer
Test layer include python modules with tests and pytest fixtures.

That layer placed in `tests` directory of project dir: [mobile tests](../tests/mobile_tests) 
that can include subdirectories and modules by test types or scope

There are a few rules that we hold:

1. Test module name should starts from `test_`
1. Test Class name should starts from `Test`
1. Test function should starts from `test`
1. Place fixtures in `conftest.py` on test layer when this fixture can be reused from different packages, modules
1. Place fixture in local python test module/conftest file when fixture used by single test/module
1. Tests function use actions from: steps layer calls (page steps, global steps or navigation steps)
 
Code sample (based on functional tests):
```python
import pytest

from common.facade import logger
from sample import mobile


@pytest.mark.usefixtures("start_mobile_session")
@pytest.mark.C00001
def test_mobile_temperature_unit_switch():
    """
    Test to check switching of temperature unit
    """
    dashboard_page = mobile.navigation_steps.navigate_to_main_page()

    logger.log_step("Set Celsius unit in settings screen")
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
```
