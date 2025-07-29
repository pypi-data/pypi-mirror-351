"""BEMServer API client tests"""

import pytest

from bemserver_api_client import BEMServerApiClient
from bemserver_api_client.authentication import BearerTokenAuth, HTTPBasicAuth
from bemserver_api_client.client import REQUIRED_API_VERSION
from bemserver_api_client.exceptions import BEMServerAPIVersionError
from bemserver_api_client.request import BEMServerApiClientRequest
from bemserver_api_client.resources import RESOURCES_MAP


class TestAPIClient:
    def test_api_client_auth_http_basic(self):
        ret = BEMServerApiClient.make_http_basic_auth("chuck@test.com", "N0rr1s")
        assert isinstance(ret, HTTPBasicAuth)
        assert isinstance(ret.username, bytes)
        assert isinstance(ret.password, bytes)
        assert ret.username.decode(encoding="utf-8") == "chuck@test.com"
        assert ret.password.decode(encoding="utf-8") == "N0rr1s"

    def test_api_client_auth_bearer_token(self):
        access_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
            "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT"
        )
        ret = BEMServerApiClient.make_bearer_token_auth(access_token)
        assert isinstance(ret, BearerTokenAuth)
        assert ret.access_token == access_token
        assert ret.refresh_token is None

        refresh_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
            "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT"
        )
        ret = BEMServerApiClient.make_bearer_token_auth(access_token, refresh_token)
        assert isinstance(ret, BearerTokenAuth)
        assert ret.access_token == access_token
        assert ret.refresh_token == refresh_token

    def test_api_client_class(self):
        apicli = BEMServerApiClient("localhost:5050")
        assert apicli.use_ssl
        assert apicli.base_uri_prefix == "http"
        assert apicli.uri_prefix == "https://"
        assert apicli.base_uri == "https://localhost:5050"
        apicli.use_ssl = False
        assert apicli.uri_prefix == "http://"
        assert apicli.base_uri == "http://localhost:5050"

        apicli.base_uri_prefix = "http+mock"
        assert apicli.uri_prefix == "http+mock://"
        assert apicli.base_uri == "http+mock://localhost:5050"
        apicli.use_ssl = True
        assert apicli.uri_prefix == "https+mock://"
        assert apicli.base_uri == "https+mock://localhost:5050"

        assert isinstance(apicli._request_manager, BEMServerApiClientRequest)

    def test_api_client_set_authentication_method(self):
        api_cli = BEMServerApiClient("localhost:5050")
        assert api_cli._request_manager._session.auth is None

        auth_method = BEMServerApiClient.make_http_basic_auth("user@mail.com", "pwd")
        api_cli.set_authentication_method(auth_method)
        assert auth_method == api_cli._request_manager._session.auth

        access_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
            "-rpkjK19GUy0Fgrkm_pGHi8XghjWM"
        )
        auth_method = BEMServerApiClient.make_bearer_token_auth(access_token)
        assert auth_method.refresh_tokens_callback is None
        api_cli.set_authentication_method(auth_method)
        assert auth_method.refresh_tokens_callback is not None
        assert auth_method == api_cli._request_manager._session.auth

    def test_api_client_resources(self):
        assert len(RESOURCES_MAP) == 57

        apicli = BEMServerApiClient("localhost:5050")

        for resource_name, resource_cls in RESOURCES_MAP.items():
            assert resource_cls.client_entrypoint is not None
            assert hasattr(apicli, resource_name)
            assert isinstance(getattr(apicli, resource_name), resource_cls)

        assert not hasattr(apicli, "whatever_resources_that_does_not_exist")
        with pytest.raises(AttributeError):
            apicli.whatever_resources_that_does_not_exist.get()

    def test_api_client_required_api_version_manual(self):
        req_version_min = REQUIRED_API_VERSION["min"]
        v = f"{req_version_min.major}.{req_version_min.minor}.42"
        BEMServerApiClient.check_api_version(str(v))

        # API version not compatible with client.
        with pytest.raises(BEMServerAPIVersionError):
            BEMServerApiClient.check_api_version("1.0.0")

        # Invalid API versionning.
        with pytest.raises(BEMServerAPIVersionError):
            BEMServerApiClient.check_api_version(None)
        with pytest.raises(BEMServerAPIVersionError):
            BEMServerApiClient.check_api_version("invalid")

    def test_api_client_required_api_version_auto_check(self, mock_request):
        host = "localhost:5000"
        auto_check = True
        req_mngr = mock_request

        BEMServerApiClient(host, auto_check=auto_check, request_manager=req_mngr)

        # API version not compatible with client.
        with pytest.raises(BEMServerAPIVersionError):
            BEMServerApiClient(host, auto_check=auto_check, request_manager=req_mngr)

        # Invalid API versionning.
        with pytest.raises(BEMServerAPIVersionError):
            BEMServerApiClient(host, auto_check=auto_check, request_manager=req_mngr)
