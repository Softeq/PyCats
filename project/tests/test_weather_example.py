import pytest

from common.facade import logger
from project.api.endpoints.daily_weather_endpoint import DailyWeatherEndpointBuilder
from project.api.steps.weather_api_steps import compare_api_weather_with_ui
from project import mobile, web


@pytest.mark.parametrize('city', ['San Jose', "Los Angeles"])
@pytest.mark.usefixtures('open_main_page')
def test_weather_api(api_token, city):
    logger.log_step(f"Open Main Page and search city {city}")
    main_steps = web.pages.MainPageSteps()
    main_steps.search_city(city, select_city=True)

    logger.log_step("Getting weather data from city details page")
    details_steps = web.pages.CityDetailsSteps()
    details_steps.verify_selected_city(city=city)
    weather_info = details_steps.get_weather_info()

    logger.log_step("Compare UI weather with API weather data")
    compare_api_weather_with_ui(city, api_token, weather_info)


@pytest.mark.usefixtures("start_mobile_session")
@pytest.mark.mabile_sample
@pytest.mark.parametrize('city', ['San Jose', "Los Angeles"])
def test_weather_mobile(api_token, city):
    """
    Test to check temperature from api is same with mobile app (use different sources, so results could be failed)

    Steps:
    1. Open Weather app and navigate to main page
    2. Add {city} location to profile and check selected city
    3. Get current temperature from api for {city} lcoation
    4. Compare APU result with mobile app result for selected location
    """
    mobile.navigation_steps.navigate_to_main_page()

    logger.log_step("Add city - {}".format(city))
    weather_page = mobile.global_steps.add_location(city=city)
    weather_page.verify_selected_city(value=city)

    logger.log_step("Get current temperature from api")
    api_result = DailyWeatherEndpointBuilder().get_weather_details(city=city, token=api_token, units='metric')

    logger.log_step("Verify current temperature for city - {}".format(city))
    weather_page.verify_current_temperature(value=str(int(api_result["main"]["temp"])))
