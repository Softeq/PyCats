import pytest

from common.facade import logger
from project.api.steps.weather_api_steps import compare_api_weather_with_ui
from project.web.steps.page_object_steps.pages.city_details import CityDetailsSteps
from project.web.steps.page_object_steps.pages.main import MainPageSteps


@pytest.mark.usefixtures("open_browser")
@pytest.mark.parametrize('city', ['San Jose', "Los Angeles"])
@pytest.mark.usefixtures('open_main_page')
def test_weather_api(api_token, city):
    logger.log_step(f"Open Main Page and search city {city}")
    main_steps = MainPageSteps()
    main_steps.search_city(city, select_city=True)

    logger.log_step("Getting weather data from city details page")
    details_steps = CityDetailsSteps()
    details_steps.verify_selected_city(city=city)
    weather_info = details_steps.get_weather_info()

    logger.log_step("Compare UI weather with API weather data")
    compare_api_weather_with_ui(city, api_token, weather_info)
