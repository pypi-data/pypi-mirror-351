"""BEMServer authentication methods tests"""

from requests.models import Request

from bemserver_api_client.authentication import BearerTokenAuth


class TestAPIAuthentication:
    def test_api_auth_bearer_token(self):
        access_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
            "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_AT"
        )
        bta = BearerTokenAuth(access_token)
        assert bta.access_token == access_token
        assert bta.refresh_token is None
        assert not bta.do_refresh
        assert bta.refresh_tokens_callback is None
        assert bta._after_refresh_tokens_callback is None

        req = bta(Request())
        assert hasattr(req, "headers")
        assert "Authorization" in req.headers
        assert req.headers["Authorization"] == f"Bearer {access_token}"

        bta.do_refresh = True
        req = bta(Request())
        assert hasattr(req, "headers")
        assert "Authorization" not in req.headers

        refresh_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.uJKHM4XyWv1bC_"
            "-rpkjK19GUy0Fgrkm_pGHi8XghjWM_RT"
        )
        bta = BearerTokenAuth(access_token, refresh_token)
        assert bta.access_token == access_token
        assert bta.refresh_token == refresh_token
        assert not bta.do_refresh

        req = bta(Request())
        assert hasattr(req, "headers")
        assert "Authorization" in req.headers
        assert req.headers["Authorization"] == f"Bearer {access_token}"

        bta.do_refresh = True
        req = bta(Request())
        assert hasattr(req, "headers")
        assert "Authorization" in req.headers
        assert req.headers["Authorization"] == f"Bearer {refresh_token}"

        def after_refresh_tokens_external_callback(
            new_access_token, new_refresh_token=None
        ):
            assert new_access_token == f"{access_token}2"
            assert new_refresh_token == f"{refresh_token}2"

        bta = BearerTokenAuth(
            access_token,
            refresh_token,
            after_refresh_tokens_external_callback=after_refresh_tokens_external_callback,
        )
        assert bta.access_token == access_token
        assert bta.refresh_token == refresh_token
        assert not bta.do_refresh
        assert bta.refresh_tokens_callback is None
        assert (
            bta._after_refresh_tokens_callback == after_refresh_tokens_external_callback
        )
        bta.after_refresh_tokens_callback(f"{access_token}2", f"{refresh_token}2")
        assert bta.access_token == f"{access_token}2"
        assert bta.refresh_token == f"{refresh_token}2"
