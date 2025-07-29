"""BEMServer API client notifications resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.notifications import NotificationResources
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesNotifications:
    def test_api_client_resources_notifications(self):
        assert issubclass(NotificationResources, BaseResources)
        assert NotificationResources.endpoint_base_uri == "/notifications/"
        assert NotificationResources.disabled_endpoints == []
        assert NotificationResources.client_entrypoint == "notifications"

    def test_api_client_resources_notifications_endpoints(self, mock_request):
        notif_res = NotificationResources(mock_request)

        resp = notif_res.count_by_campaign(user_id=42)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.etag == "734ab7a416e0c0b1b1ded1a96cd53425f9bcd7f8"
        assert resp.data["total"] == 1

        resp = notif_res.mark_all_as_read(user_id=42)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
