"""BEMServer API client resources

/weather_timeseries_by_sites/ endpoints
"""

from .base import BaseResources


class WeatherTimseriesBySiteResources(BaseResources):
    endpoint_base_uri = "/weather_timeseries_by_sites/"
    client_entrypoint = "weather_ts_by_sites"
