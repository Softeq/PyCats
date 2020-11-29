from common.facade.api import BaseRequestModel, BaseResponseModel, endpoint_factory
from common.facade.api import SKIP, pycats_dataclass
from common.facade import raw_config, logger


# TODO - find solution to set dataclass fields properly after initialization
def query_builder(city, token, units='imperial'):
    return f'q={city}&appid={token}&units={units}'


@pycats_dataclass
class DailyWeatherEndpointBuilder:
    @pycats_dataclass
    class _DailyWeatherRequestModel(BaseRequestModel):
        resource: str = 'weather'
        headers = {"Accept": "application/json"}
        post_data = None
        put_data = None
        patch_data = None
        delete_data = None
        params = None
        allowed_methods = ("get",)

    @pycats_dataclass
    class _DailyWeatherResponseModel(BaseResponseModel):
        status_code = 200
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        get_data = {"coord": {"lon": SKIP, "lat": SKIP},
                    "weather": [{"id": SKIP, "main": SKIP, "description": SKIP, "icon": SKIP}],
                    "base": "stations",
                    "main": {"temp": SKIP, "feels_like": SKIP, "temp_min": SKIP, "temp_max": SKIP, "pressure": SKIP,
                             "humidity": SKIP}, "visibility": SKIP, "wind": {"speed": SKIP},
                    "clouds": {"all": SKIP}, "dt": SKIP,
                    "sys": {"type": SKIP, "id": SKIP, "country": SKIP, "sunrise": SKIP, "sunset": SKIP},
                    "timezone": SKIP, "id": SKIP, "name": SKIP, "cod": SKIP}
        post_data = None
        put_data = None
        delete_data = None
        patch_data = None
        error_data = None
        custom_checkers = []

    _DailyWeatherResponseModel.configure_validator()
    endpoint = endpoint_factory(raw_config.project_settings.web_api_url, __qualname__,
                                _DailyWeatherRequestModel, _DailyWeatherResponseModel)

    def get_weather_details(self, city, token):
        logger.info("Get weather details")
        self.endpoint.request_model.params = query_builder(city, token)
        result = self.endpoint.get()
        return result.get_data
