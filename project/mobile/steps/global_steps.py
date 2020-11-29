from project.mobile.steps.pages.weather import WeatherSteps
from project.mobile.steps.pages.add_location import AddLocationSteps


def add_location(city):
    weather_steps = WeatherSteps()
    weather_steps.click_add_location()

    add_location_page = AddLocationSteps()
    add_location_page.select_location_by_value(value=city)
    return WeatherSteps()
