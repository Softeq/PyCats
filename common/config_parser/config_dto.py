from dataclasses import dataclass


@dataclass
class APIValidationDTO:
    check_status_code: bool
    check_headers: bool
    check_body: bool
    check_is_field_missing: bool


@dataclass
class WebDriverSettingsDTO:
    webdriver_folder: str
    webdriver_default_wait_time: int
    webdriver_implicit_wait_time: int
    selenium_server_executable: str
    chrome_driver_name: str
    firefox_driver_name: str
    browser: str
    driver_path: str
    stop_server: bool
    chrome_options: list
