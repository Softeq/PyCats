__all__ = ['add_location']

from project.mobile.steps.page_steps.pages.weather import WeatherSteps
from project.mobile.steps.page_steps.pages.add_location import AddLocationSteps


def add_location(city):
    weather_steps = WeatherSteps()
    weather_steps.click_add_location()

    add_location_page = AddLocationSteps()
    add_location_page.select_location_by_value(value=city)
    return WeatherSteps()
