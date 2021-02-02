__all__ = ['navigate_to_main_page']

from common.facade import logger

from project.mobile.src.confirmations.location_permission import LocationPermissionAndroid
from project.mobile.steps.page_steps.pages.setup_notification import SetupNotificationSteps
from project.mobile.steps.page_steps.pages.setup_location import SetupLocationSteps
from project.mobile.steps.page_steps.pages.weather import WeatherSteps


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
