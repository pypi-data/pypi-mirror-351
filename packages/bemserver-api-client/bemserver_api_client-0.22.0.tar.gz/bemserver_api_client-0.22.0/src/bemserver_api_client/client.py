"""BEMServer API client"""

import logging

from packaging.version import InvalidVersion, Version

from .authentication import BearerTokenAuth, HTTPBasicAuth
from .exceptions import BEMServerAPIAuthenticationError, BEMServerAPIVersionError
from .request import BEMServerApiClientRequest
from .resources import RESOURCES_MAP

APICLI_LOGGER = logging.getLogger(__name__)

REQUIRED_API_VERSION = {
    "min": Version("0.26.0"),
    "max": Version("0.27.0"),
}


class BEMServerApiClient:
    """API client"""

    def __init__(
        self,
        host,
        use_ssl=True,
        authentication_method=None,
        uri_prefix="http",
        auto_check=False,
        request_manager=None,
    ):
        self.base_uri_prefix = uri_prefix or "http"
        self.host = host
        self.use_ssl = use_ssl

        self._request_manager = request_manager or BEMServerApiClientRequest(
            self.base_uri,
            self._ensure_bearer_token_auth_callbacks(authentication_method),
            logger=APICLI_LOGGER,
        )

        if auto_check:
            api_version = self.about.getall().data["versions"]["bemserver_api"]
            self.check_api_version(api_version)

    def __getattr__(self, name):
        try:
            # Here name value is expected to be a resource client_entrypoint value.
            return RESOURCES_MAP[name](self._request_manager)
        except KeyError as exc:
            raise AttributeError from exc

    @property
    def uri_prefix(self):
        uri_prefix = self.base_uri_prefix
        if self.use_ssl:
            uri_prefix = self.base_uri_prefix.replace("http", "https")
        return f"{uri_prefix}://"

    @property
    def base_uri(self):
        return f"{self.uri_prefix}{self.host}"

    @staticmethod
    def make_http_basic_auth(email, password):
        return HTTPBasicAuth(
            email.encode(encoding="utf-8"),
            password.encode(encoding="utf-8"),
        )

    @staticmethod
    def make_bearer_token_auth(
        access_token, refresh_token=None, after_refresh_tokens_callback=None
    ):
        return BearerTokenAuth(
            access_token,
            refresh_token=refresh_token,
            after_refresh_tokens_external_callback=after_refresh_tokens_callback,
        )

    def _ensure_bearer_token_auth_callbacks(self, authentication_method):
        # Ensure that bearer token authentication refreshes automatically
        #  its expired access token.
        if isinstance(authentication_method, BearerTokenAuth):

            def _refresh_tokens_callback():
                auth_resp = self.auth.refresh_tokens()
                if auth_resp.data["status"] == "failure":
                    raise BEMServerAPIAuthenticationError
                authentication_method.after_refresh_tokens_callback(
                    auth_resp.data["access_token"],
                    auth_resp.data["refresh_token"],
                )

            authentication_method.refresh_tokens_callback = _refresh_tokens_callback

        return authentication_method

    def set_authentication_method(self, authentication_method):
        self._request_manager.set_authentication_method(
            self._ensure_bearer_token_auth_callbacks(authentication_method)
        )

    @classmethod
    def check_api_version(cls, api_version):
        try:
            version_api = Version(str(api_version))
        except InvalidVersion as exc:
            raise BEMServerAPIVersionError(f"Invalid API version: {str(exc)}") from exc
        version_min = REQUIRED_API_VERSION["min"]
        version_max = REQUIRED_API_VERSION["max"]
        if not (version_min <= version_api < version_max):
            raise BEMServerAPIVersionError(
                f"API version ({str(version_api)}) not supported!"
                f" (expected: >={str(version_min)},<{str(version_max)})"
            )
