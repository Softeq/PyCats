__all__ = ['add_location']

from common.facade import logger
from project.mobile.steps.page_steps.pages.weather import WeatherSteps
from project.mobile.steps.page_steps.pages.add_location import AddLocationSteps


def add_location(city):
    logger.log_title(f"Add '{city}' to location list")
    weather_steps = WeatherSteps()
    weather_steps.click_add_location()

    add_location_page = AddLocationSteps()
    add_location_page.select_location_by_value(value=city)
    return WeatherSteps()
