"""BEMServer API client authentication resources tests"""

import pytest

from bemserver_api_client import BEMServerApiClient
from bemserver_api_client.authentication import BearerTokenAuth
from bemserver_api_client.exceptions import BEMServerAPIAuthenticationError
from bemserver_api_client.resources.auth import AuthenticationResources
from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesAuth:
    def test_api_client_resources_auth(self):
        assert issubclass(AuthenticationResources, BaseResources)
        assert AuthenticationResources.endpoint_base_uri == "/auth/"
        assert AuthenticationResources.disabled_endpoints == [
            "getall",
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert AuthenticationResources.client_entrypoint == "auth"

        assert hasattr(AuthenticationResources, "get_tokens")
        assert hasattr(AuthenticationResources, "refresh_tokens")

    def test_api_client_resources_auth_get_tokens(self, mock_request):
        auth_res = AuthenticationResources(mock_request)

        resp = auth_res.get_tokens("chuck@norris.com", "awesome")
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.data == {
            "status": "success",
            "access_token": (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
                "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT1"
            ),
            "refresh_token": (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
                "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT1"
            ),
        }

        resp = auth_res.get_tokens("chuck@norris.com", "useless")
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.data == {
            "status": "failure",
        }

    @pytest.mark.parametrize(
        "api_client",
        (
            {
                "auth_method": BEMServerApiClient.make_bearer_token_auth(
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT1",
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT1",
                )
            },
        ),
        indirect=True,
    )
    def test_api_client_resources_auth_refresh_tokens(self, api_client):
        assert isinstance(api_client._request_manager._session.auth, BearerTokenAuth)

        resp = api_client.auth.refresh_tokens()
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.data == {
            "status": "success",
            "access_token": (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
                "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT2"
            ),
            "refresh_token": (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
                "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT2"
            ),
        }

    @pytest.mark.parametrize(
        "api_client",
        (
            {
                "auth_method": BEMServerApiClient.make_bearer_token_auth(
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT1_expired",
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT1",
                )
            },
        ),
        indirect=True,
    )
    def test_api_client_resources_auth_refresh_tokens_auto(self, api_client):
        assert isinstance(api_client._request_manager._session.auth, BearerTokenAuth)
        assert (
            api_client._request_manager._session.auth.refresh_tokens_callback
            is not None
        )
        assert (
            api_client._request_manager._session.auth._after_refresh_tokens_callback
            is None
        )

        def after_refresh_tokens_external_callback(
            new_access_token, new_refresh_token=None
        ):
            assert new_access_token == (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
                "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT2"
            )
            assert new_refresh_token == (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
                "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT2"
            )

        api_client._request_manager._session.auth._after_refresh_tokens_callback = (
            after_refresh_tokens_external_callback
        )

        resp = api_client.users.getone(1)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "0d898370a9ce828b8e570102ad450210c892ae00"
        assert resp.data == {
            "email": "john@doe.com",
            "id": 1,
            "is_active": False,
            "is_admin": False,
            "name": "John",
        }

    @pytest.mark.parametrize(
        "api_client",
        (
            {
                "auth_method": BEMServerApiClient.make_bearer_token_auth(
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT1",
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT1_expired",
                )
            },
        ),
        indirect=True,
    )
    def test_api_client_resources_auth_refresh_tokens_invalid(self, api_client):
        assert isinstance(api_client.auth._req._session.auth, BearerTokenAuth)
        assert api_client.auth._req._session.auth.refresh_tokens_callback is not None

        with pytest.raises(BEMServerAPIAuthenticationError):
            api_client.auth.refresh_tokens()

        assert not api_client.auth._req._session.auth.do_refresh
