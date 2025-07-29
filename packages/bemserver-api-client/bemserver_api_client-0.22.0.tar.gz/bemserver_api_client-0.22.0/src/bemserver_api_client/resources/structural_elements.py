"""BEMServer API client resources

/sites/ endpoints
/buildings/ endpoints
/storeys/ endpoints
/spaces/ endpoints
/zones/ endpoints
/structural_element_properties/ endpoints
/site_properties/ endpoints
/building_properties/ endpoints
/storey_properties/ endpoints
/space_properties/ endpoints
/zone_properties/ endpoints
/site_property_data/ endpoints
/building_property_data/ endpoints
/storey_property_data/ endpoints
/space_property_data/ endpoints
/zone_property_data/ endpoints
"""

from ..enums import DegreeDaysPeriod, DegreeDaysType
from ..exceptions import BEMServerAPIClientValueError
from .base import BaseResources


class SiteResources(BaseResources):
    endpoint_base_uri = "/sites/"
    client_entrypoint = "sites"

    def download_weather_data(self, id, start_time, end_time):
        return self._req._execute(
            "PUT",
            f"{self.enpoint_uri_by_id(id)}/download_weather_data",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )

    def get_degree_days(
        self,
        id,
        start_date,
        end_date,
        *,
        period=DegreeDaysPeriod.day,
        type=DegreeDaysType.heating,
        base=18,
        unit="°C",
    ):
        if period not in list(DegreeDaysPeriod):
            raise BEMServerAPIClientValueError(f"Invalid period: {period}")
        if type not in list(DegreeDaysType):
            raise BEMServerAPIClientValueError(f"Invalid type: {type}")
        return self._req._execute(
            "GET",
            f"{self.enpoint_uri_by_id(id)}/degree_days",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "period": period.value,
                "type": type.value,
                "base": base,
                "unit": unit,
            },
        )


class BuildingResources(BaseResources):
    endpoint_base_uri = "/buildings/"
    client_entrypoint = "buildings"


class StoreyResources(BaseResources):
    endpoint_base_uri = "/storeys/"
    client_entrypoint = "storeys"


class SpaceResources(BaseResources):
    endpoint_base_uri = "/spaces/"
    client_entrypoint = "spaces"


class ZoneResources(BaseResources):
    endpoint_base_uri = "/zones/"
    client_entrypoint = "zones"


class StructuralElementPropertyResources(BaseResources):
    endpoint_base_uri = "/structural_element_properties/"
    client_entrypoint = "structural_element_properties"


class SitePropertyResources(BaseResources):
    endpoint_base_uri = "/site_properties/"
    disabled_endpoints = ["update"]
    client_entrypoint = "site_properties"


class BuildingPropertyResources(BaseResources):
    endpoint_base_uri = "/building_properties/"
    disabled_endpoints = ["update"]
    client_entrypoint = "building_properties"


class StoreyPropertyResources(BaseResources):
    endpoint_base_uri = "/storey_properties/"
    disabled_endpoints = ["update"]
    client_entrypoint = "storey_properties"


class SpacePropertyResources(BaseResources):
    endpoint_base_uri = "/space_properties/"
    disabled_endpoints = ["update"]
    client_entrypoint = "space_properties"


class ZonePropertyResources(BaseResources):
    endpoint_base_uri = "/zone_properties/"
    disabled_endpoints = ["update"]
    client_entrypoint = "zone_properties"


class SitePropertyDataResources(BaseResources):
    endpoint_base_uri = "/site_property_data/"
    client_entrypoint = "site_property_data"


class BuildingPropertyDataResources(BaseResources):
    endpoint_base_uri = "/building_property_data/"
    client_entrypoint = "building_property_data"


class StoreyPropertyDataResources(BaseResources):
    endpoint_base_uri = "/storey_property_data/"
    client_entrypoint = "storey_property_data"


class SpacePropertyDataResources(BaseResources):
    endpoint_base_uri = "/space_property_data/"
    client_entrypoint = "space_property_data"


class ZonePropertyDataResources(BaseResources):
    endpoint_base_uri = "/zone_property_data/"
    client_entrypoint = "zone_property_data"
