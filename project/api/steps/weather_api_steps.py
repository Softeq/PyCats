from project.api.api_utils import get_ui_time_from_api
from project.api.endpoints.daily_weather_endpoint import DailyWeatherEndpointBuilder


def compare_api_weather_with_ui(city, token, ui_weather_info):
    api_result = DailyWeatherEndpointBuilder().get_weather_details(city, token)
    result_dict = {"pressure": str(api_result["main"]["pressure"]),
                   "humidity": str(api_result["main"]["humidity"]),
                   "sunrise": get_ui_time_from_api(api_result["sys"]["sunrise"]),
                   "sunset": get_ui_time_from_api(api_result["sys"]["sunset"]),
                   }
    assert result_dict == ui_weather_info, \
        f"Data from api: '{result_dict}', data from UI: '{ui_weather_info}'"
