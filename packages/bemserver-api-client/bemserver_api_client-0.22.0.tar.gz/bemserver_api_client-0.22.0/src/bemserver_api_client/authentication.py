"""Manage bearer token (JWT) authentication method"""

from requests.auth import (
    AuthBase,
    HTTPBasicAuth,  # noqa
)


class BearerTokenAuth(AuthBase):
    """Set bearer access/refresh token authentication to the given Request object."""

    def __init__(
        self,
        access_token,
        refresh_token=None,
        refresh_tokens_callback=None,
        after_refresh_tokens_external_callback=None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.do_refresh = False
        self.refresh_tokens_callback = refresh_tokens_callback
        self._after_refresh_tokens_callback = after_refresh_tokens_external_callback

    def __call__(self, r):
        # Modify and return the request with the bearer authorization header.
        token = self.refresh_token if self.do_refresh else self.access_token
        if token is not None:
            r.headers["Authorization"] = f"Bearer {token}"
        return r

    def after_refresh_tokens_callback(self, access_token, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token

        if self._after_refresh_tokens_callback is not None:
            self._after_refresh_tokens_callback(access_token, refresh_token)
