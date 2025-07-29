"""BEMServer API client users resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.users import (
    UserByUserGroupResources,
    UserGroupResources,
    UserResources,
)
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesUsers:
    def test_api_client_resources_users(self):
        assert issubclass(UserResources, BaseResources)
        assert UserResources.endpoint_base_uri == "/users/"
        assert UserResources.disabled_endpoints == []
        assert UserResources.client_entrypoint == "users"
        assert hasattr(UserResources, "set_admin")
        assert hasattr(UserResources, "set_active")

        assert issubclass(UserGroupResources, BaseResources)
        assert UserGroupResources.endpoint_base_uri == "/user_groups/"
        assert UserGroupResources.disabled_endpoints == []
        assert UserGroupResources.client_entrypoint == "user_groups"

        assert issubclass(UserByUserGroupResources, BaseResources)
        assert UserByUserGroupResources.endpoint_base_uri == "/users_by_user_groups/"
        assert UserByUserGroupResources.disabled_endpoints == ["update"]
        assert UserByUserGroupResources.client_entrypoint == "user_by_user_groups"

    def test_api_client_resources_users_endpoints(self, mock_request):
        users_res = UserResources(mock_request)
        resp = users_res.set_admin(0, True)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 204

        resp = users_res.set_active(0, True)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 204
