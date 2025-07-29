"""BEMServer API client resources

/auth/ endpoint
"""

from .base import BaseResources


class AuthenticationResources(BaseResources):
    endpoint_base_uri = "/auth/"
    disabled_endpoints = ["getall", "getone", "create", "update", "delete"]
    client_entrypoint = "auth"

    def get_tokens(self, email, password):
        payload = {
            "email": email,
            "password": password,
        }
        return self._req._execute(
            "POST", f"{self.endpoint_base_uri}token", json=payload, try_refresh=False
        )

    def refresh_tokens(self):
        # TODO: find a way to lock all other requests while refreshing tokens.
        #  (meanwhile tokens may be refreshed multiple times...)
        self._req.is_authentication_refreshing = True
        try:
            ret = self._req._execute(
                "POST", f"{self.endpoint_base_uri}token/refresh", try_refresh=False
            )
        except Exception as exc:
            raise exc
        finally:
            self._req.is_authentication_refreshing = False
        return ret
