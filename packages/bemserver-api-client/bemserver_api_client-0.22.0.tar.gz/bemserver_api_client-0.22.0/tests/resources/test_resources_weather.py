"""BEMServer API client weather resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.weather import WeatherTimseriesBySiteResources


class TestAPIClientResourcesWeather:
    def test_api_client_resources_weather(self):
        assert issubclass(WeatherTimseriesBySiteResources, BaseResources)
        assert WeatherTimseriesBySiteResources.endpoint_base_uri == (
            "/weather_timeseries_by_sites/"
        )
        assert WeatherTimseriesBySiteResources.disabled_endpoints == []
        assert WeatherTimseriesBySiteResources.client_entrypoint == (
            "weather_ts_by_sites"
        )
