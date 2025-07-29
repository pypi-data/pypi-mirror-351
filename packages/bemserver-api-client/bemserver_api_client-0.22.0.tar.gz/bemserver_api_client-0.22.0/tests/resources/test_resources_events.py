"""BEMServer API client events resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.events import (
    EventByBuildingResources,
    EventBySiteResources,
    EventBySpaceResources,
    EventByStoreyResources,
    EventByZoneResources,
    EventCategoryByUserResources,
    EventCategoryResources,
    EventResources,
)
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesEvents:
    def test_api_client_resources_events(self):
        assert issubclass(EventResources, BaseResources)
        assert EventResources.endpoint_base_uri == "/events/"
        assert EventResources.disabled_endpoints == []
        assert EventResources.client_entrypoint == "events"

        assert issubclass(EventCategoryResources, BaseResources)
        assert EventCategoryResources.endpoint_base_uri == "/event_categories/"
        assert EventCategoryResources.disabled_endpoints == []
        assert EventCategoryResources.client_entrypoint == "event_categories"

        assert issubclass(EventCategoryByUserResources, BaseResources)
        assert EventCategoryByUserResources.endpoint_base_uri == (
            "/event_categories_by_users/"
        )
        assert EventCategoryByUserResources.disabled_endpoints == []
        assert EventCategoryByUserResources.client_entrypoint == (
            "event_categories_by_users"
        )

        assert issubclass(EventBySiteResources, BaseResources)
        assert EventBySiteResources.endpoint_base_uri == "/events_by_sites/"
        assert EventBySiteResources.disabled_endpoints == ["update"]
        assert EventBySiteResources.client_entrypoint == "event_by_sites"

        assert issubclass(EventByBuildingResources, BaseResources)
        assert EventByBuildingResources.endpoint_base_uri == "/events_by_buildings/"
        assert EventByBuildingResources.disabled_endpoints == ["update"]
        assert EventByBuildingResources.client_entrypoint == "event_by_buildings"

        assert issubclass(EventByStoreyResources, BaseResources)
        assert EventByStoreyResources.endpoint_base_uri == "/events_by_storeys/"
        assert EventByStoreyResources.disabled_endpoints == ["update"]
        assert EventByStoreyResources.client_entrypoint == "event_by_storeys"

        assert issubclass(EventBySpaceResources, BaseResources)
        assert EventBySpaceResources.endpoint_base_uri == "/events_by_spaces/"
        assert EventBySpaceResources.disabled_endpoints == ["update"]
        assert EventBySpaceResources.client_entrypoint == "event_by_spaces"

        assert issubclass(EventByZoneResources, BaseResources)
        assert EventByZoneResources.endpoint_base_uri == "/events_by_zones/"
        assert EventByZoneResources.disabled_endpoints == ["update"]
        assert EventByZoneResources.client_entrypoint == "event_by_zones"

    def test_api_client_resources_events_endpoints(self, mock_request):
        event_res = EventResources(mock_request)

        resp = event_res.getall(page_size=5)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {
            "total": 12,
            "total_pages": 3,
            "first_page": 1,
            "last_page": 3,
            "page": 1,
            "next_page": 2,
        }
        assert resp.etag == "5e848c32d0338815a739fa470e2d518aba47a077"
        assert len(resp.data) == 5
