"""BEMServer API client resources

/event_categories/ endpoints
/event_categories_by_users/ endpoints
/events/ endpoints
/events_by_sites/ endpoints
/events_by_buildings/ endpoints
/events_by_storeys/ endpoints
/events_by_spaces/ endpoints
/events_by_zones/ endpoints
"""

from .base import BaseResources


class EventCategoryResources(BaseResources):
    endpoint_base_uri = "/event_categories/"
    client_entrypoint = "event_categories"


class EventCategoryByUserResources(BaseResources):
    endpoint_base_uri = "/event_categories_by_users/"
    client_entrypoint = "event_categories_by_users"


class EventResources(BaseResources):
    endpoint_base_uri = "/events/"
    client_entrypoint = "events"


class EventBySiteResources(BaseResources):
    endpoint_base_uri = "/events_by_sites/"
    disabled_endpoints = ["update"]
    client_entrypoint = "event_by_sites"


class EventByBuildingResources(BaseResources):
    endpoint_base_uri = "/events_by_buildings/"
    disabled_endpoints = ["update"]
    client_entrypoint = "event_by_buildings"


class EventByStoreyResources(BaseResources):
    endpoint_base_uri = "/events_by_storeys/"
    disabled_endpoints = ["update"]
    client_entrypoint = "event_by_storeys"


class EventBySpaceResources(BaseResources):
    endpoint_base_uri = "/events_by_spaces/"
    disabled_endpoints = ["update"]
    client_entrypoint = "event_by_spaces"


class EventByZoneResources(BaseResources):
    endpoint_base_uri = "/events_by_zones/"
    disabled_endpoints = ["update"]
    client_entrypoint = "event_by_zones"
