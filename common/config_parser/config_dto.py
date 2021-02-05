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
    default_wait_time: int
    implicit_wait_time: int
    selenium_server_executable: str
    chrome_driver_name: str
    firefox_driver_name: str
    browser: str
    driver_path: str


@dataclass
class MobileDriverSettingsDTO:
    appium_server_path: str
    node_executable_path: str
    default_wait_time: int
    implicit_wait_time: int
    platform: str
    ios_udid: str
    ipa_path: str
    android_udid: str
    android_package: str
    android_activity: str
