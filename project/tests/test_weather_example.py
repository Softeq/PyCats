import pytest

from common.scaf import logger
from project.api.steps.weather_api_steps import compare_api_weather_with_ui
from project.web.steps.city_details import CityDetailsSteps
from project.web.steps.main import MainPageSteps
from project.web.steps.search_result import SearchResultSteps


@pytest.mark.parametrize('city', ['San Jose', "Los Angeles"])
def test_weather_api(main_page, api_token,  city):
    logger.log_step(f"Open Main Page and search city {city}")
    main_steps = MainPageSteps()
    main_steps.search_city(city)

    logger.log_step("Click on the first search result")
    search_result_step = SearchResultSteps()
    search_result_step.click_first_result()

    logger.log_step("Getting weather data from city details page")
    details_steps = CityDetailsSteps()
    weather_info = details_steps.get_weather_info()

    logger.log_step("Compare UI weather with API weather data")
    compare_api_weather_with_ui(city, api_token, weather_info)
