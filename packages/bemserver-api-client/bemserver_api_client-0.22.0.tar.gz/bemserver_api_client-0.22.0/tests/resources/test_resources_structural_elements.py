"""BEMServer API client structural element resources tests"""

import pytest

from tests.conftest import FakeEnum

from bemserver_api_client.enums import DegreeDaysPeriod, DegreeDaysType
from bemserver_api_client.exceptions import BEMServerAPIClientValueError
from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.structural_elements import (
    BuildingPropertyDataResources,
    BuildingPropertyResources,
    BuildingResources,
    SitePropertyDataResources,
    SitePropertyResources,
    SiteResources,
    SpacePropertyDataResources,
    SpacePropertyResources,
    SpaceResources,
    StoreyPropertyDataResources,
    StoreyPropertyResources,
    StoreyResources,
    StructuralElementPropertyResources,
    ZonePropertyDataResources,
    ZonePropertyResources,
    ZoneResources,
)
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesStructuralElements:
    def test_api_client_resources_structural_elements(self):
        assert issubclass(SiteResources, BaseResources)
        assert SiteResources.endpoint_base_uri == "/sites/"
        assert SiteResources.disabled_endpoints == []
        assert SiteResources.client_entrypoint == "sites"
        assert hasattr(SiteResources, "download_weather_data")
        assert hasattr(SiteResources, "get_degree_days")

        assert issubclass(BuildingResources, BaseResources)
        assert BuildingResources.endpoint_base_uri == "/buildings/"
        assert BuildingResources.disabled_endpoints == []
        assert BuildingResources.client_entrypoint == "buildings"

        assert issubclass(StoreyResources, BaseResources)
        assert StoreyResources.endpoint_base_uri == "/storeys/"
        assert StoreyResources.disabled_endpoints == []
        assert StoreyResources.client_entrypoint == "storeys"

        assert issubclass(SpaceResources, BaseResources)
        assert SpaceResources.endpoint_base_uri == "/spaces/"
        assert SpaceResources.disabled_endpoints == []
        assert SpaceResources.client_entrypoint == "spaces"

        assert issubclass(ZoneResources, BaseResources)
        assert ZoneResources.endpoint_base_uri == "/zones/"
        assert ZoneResources.disabled_endpoints == []
        assert ZoneResources.client_entrypoint == "zones"

        assert issubclass(StructuralElementPropertyResources, BaseResources)
        assert StructuralElementPropertyResources.endpoint_base_uri == (
            "/structural_element_properties/"
        )
        assert StructuralElementPropertyResources.disabled_endpoints == []
        assert StructuralElementPropertyResources.client_entrypoint == (
            "structural_element_properties"
        )

        assert issubclass(SitePropertyResources, BaseResources)
        assert SitePropertyResources.endpoint_base_uri == "/site_properties/"
        assert SitePropertyResources.disabled_endpoints == ["update"]
        assert SitePropertyResources.client_entrypoint == "site_properties"

        assert issubclass(BuildingPropertyResources, BaseResources)
        assert BuildingPropertyResources.endpoint_base_uri == "/building_properties/"
        assert BuildingPropertyResources.disabled_endpoints == ["update"]
        assert BuildingPropertyResources.client_entrypoint == "building_properties"

        assert issubclass(StoreyPropertyResources, BaseResources)
        assert StoreyPropertyResources.endpoint_base_uri == "/storey_properties/"
        assert StoreyPropertyResources.disabled_endpoints == ["update"]
        assert StoreyPropertyResources.client_entrypoint == "storey_properties"

        assert issubclass(SpacePropertyResources, BaseResources)
        assert SpacePropertyResources.endpoint_base_uri == "/space_properties/"
        assert SpacePropertyResources.disabled_endpoints == ["update"]
        assert SpacePropertyResources.client_entrypoint == "space_properties"

        assert issubclass(ZonePropertyResources, BaseResources)
        assert ZonePropertyResources.endpoint_base_uri == "/zone_properties/"
        assert ZonePropertyResources.disabled_endpoints == ["update"]
        assert ZonePropertyResources.client_entrypoint == "zone_properties"

        assert issubclass(SitePropertyDataResources, BaseResources)
        assert SitePropertyDataResources.endpoint_base_uri == "/site_property_data/"
        assert SitePropertyDataResources.disabled_endpoints == []
        assert SitePropertyDataResources.client_entrypoint == "site_property_data"

        assert issubclass(BuildingPropertyDataResources, BaseResources)
        assert BuildingPropertyDataResources.endpoint_base_uri == (
            "/building_property_data/"
        )
        assert BuildingPropertyDataResources.disabled_endpoints == []
        assert BuildingPropertyDataResources.client_entrypoint == (
            "building_property_data"
        )

        assert issubclass(StoreyPropertyDataResources, BaseResources)
        assert StoreyPropertyDataResources.endpoint_base_uri == (
            "/storey_property_data/"
        )
        assert StoreyPropertyDataResources.disabled_endpoints == []
        assert StoreyPropertyDataResources.client_entrypoint == "storey_property_data"

        assert issubclass(SpacePropertyDataResources, BaseResources)
        assert SpacePropertyDataResources.endpoint_base_uri == "/space_property_data/"
        assert SpacePropertyDataResources.disabled_endpoints == []
        assert SpacePropertyDataResources.client_entrypoint == "space_property_data"

        assert issubclass(ZonePropertyDataResources, BaseResources)
        assert ZonePropertyDataResources.endpoint_base_uri == "/zone_property_data/"
        assert ZonePropertyDataResources.disabled_endpoints == []
        assert ZonePropertyDataResources.client_entrypoint == "zone_property_data"

    def test_api_client_resources_sites_endpoints(self, mock_request):
        sites_res = SiteResources(mock_request)

        # Call a download weather data from an external weather service.
        resp = sites_res.download_weather_data(
            1,
            "2020-01-01T00:00:00+00:00",
            "2020-01-01T00:30:00+00:00",
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 204
        assert resp.is_json
        assert not resp.is_csv
        assert resp.pagination == {}
        assert resp.etag == ""
        assert resp.data == {}

        # Get degree days for a site.
        dd_json = {
            "2020-01-01T00:00:00+00:00": 7.1,
            "2020-01-02T00:00:00+00:00": 7.2,
            "2020-01-03T00:00:00+00:00": 7.3,
            "2020-01-04T00:00:00+00:00": 7.4,
        }
        resp = sites_res.get_degree_days(
            1,
            "2020-01-01",
            "2020-01-05",
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert not resp.is_csv
        assert "degree_days" in resp.data
        assert len(resp.data["degree_days"].keys()) == len(dd_json.keys())
        for k, v in resp.data["degree_days"].items():
            assert k in dd_json
            assert v == dd_json[k]

        dd_json = {
            "2020-07-01T00:00:00+00:00": 297.4,
        }
        resp = sites_res.get_degree_days(
            1,
            "2020-07-01",
            "2020-08-01",
            period=DegreeDaysPeriod.month,
            type=DegreeDaysType.cooling,
            base=24,
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert not resp.is_csv
        assert len(resp.data["degree_days"].keys()) == len(dd_json.keys())
        for k, v in resp.data["degree_days"].items():
            assert k in dd_json
            assert v == dd_json[k]

    def test_api_client_resources_sites_endpoints_errors(self, mock_request):
        sites_res = SiteResources(mock_request)

        for bad_period in [None, "hour", "other", 42, FakeEnum.b]:
            with pytest.raises(
                BEMServerAPIClientValueError,
                match=f"Invalid period: {bad_period}",
            ):
                sites_res.get_degree_days(
                    1,
                    "2020-01-01T00:00:00+00:00",
                    "2020-01-05T00:00:00+00:00",
                    period=bad_period,
                )

        for bad_type in [None, "other", 42, FakeEnum.b]:
            with pytest.raises(
                BEMServerAPIClientValueError,
                match=f"Invalid type: {bad_type}",
            ):
                sites_res.get_degree_days(
                    1,
                    "2020-01-01T00:00:00+00:00",
                    "2020-01-05T00:00:00+00:00",
                    type=bad_type,
                )
