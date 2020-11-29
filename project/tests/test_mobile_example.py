import pytest

from common.facade import logger
from project.api.endpoints.daily_weather_endpoint import DailyWeatherEndpointBuilder
from project.mobile.steps.global_steps import add_location
from project.mobile.steps.navigation_steps import navigate_to_main_page


@pytest.mark.usefixtures("start_mobile_session")
@pytest.mark.mabile_sample
@pytest.mark.parametrize('city', ['San Jose', "Los Angeles"])
def test_mobile_api(api_token, city):
    """
    Test to check temperature from api is same with mobile app (use different sources, so results could be failed)

    Steps:
    1. Open Weather app and navigate to main page
    2. Add {city} location to profile and check selected city
    3. Get current temperature from api for {city} lcoation
    4. Compare APU result with mobile app result for selected location
    """

    navigate_to_main_page()

    logger.log_step("Add city - {}".format(city))
    weather_steps = add_location(city=city)
    weather_steps.verify_selected_city(value=city)

    logger.log_step("Get current temperature from api")
    api_result = DailyWeatherEndpointBuilder().get_weather_details(city=city, token=api_token, units='metric')

    logger.log_step("Verify current temperature for city - {}".format(city))
    weather_steps.verify_current_temperature(value=str(int(api_result["main"]["temp"])))
