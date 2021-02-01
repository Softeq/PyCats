from common._webdriver_qa_api.core.utils import assert_should_be_equal
from common.facade import logger
from project.api.endpoints.daily_weather_endpoint import DailyWeatherEndpointBuilder


def compare_api_weather_with_ui(city, token, ui_weather_info):
    logger.log_title(f"Get weather information from api and compare with web results.")

    api_result = DailyWeatherEndpointBuilder().get_weather_details(city, token)
    result_dict = {"pressure": str(api_result["main"]["pressure"]),
                   "humidity": str(api_result["main"]["humidity"]),
                   }
    assert_should_be_equal(actual_value=result_dict, expected_value=ui_weather_info,
                           message=f"Data from api: '{result_dict}', data from UI: '{ui_weather_info}'")
