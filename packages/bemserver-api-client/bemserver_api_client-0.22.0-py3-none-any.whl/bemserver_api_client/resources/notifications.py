"""BEMServer API client resources

/notifications/ endpoints
"""

from .base import BaseResources


class NotificationResources(BaseResources):
    endpoint_base_uri = "/notifications/"
    client_entrypoint = "notifications"

    def count_by_campaign(self, *, etag=None, **kwargs):
        endpoint = f"{self.endpoint_base_uri}count_by_campaign"
        return self._req.getall(endpoint, etag=etag, params=kwargs)

    def mark_all_as_read(self, **kwargs):
        endpoint = f"{self.endpoint_base_uri}mark_all_as_read"
        return self._req._execute("PUT", endpoint, params=kwargs)
