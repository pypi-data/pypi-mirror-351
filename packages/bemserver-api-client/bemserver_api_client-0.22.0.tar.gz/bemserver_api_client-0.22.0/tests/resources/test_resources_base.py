"""BEMServer API client resources tests"""

from contextlib import nullcontext as not_raises

import pytest

from bemserver_api_client.exceptions import (
    BEMServerAPIAuthenticationError,
    BEMServerAPIAuthorizationError,
    BEMServerAPIInternalError,
    BEMServerAPINotFoundError,
    BEMServerAPINotModified,
    BEMServerAPIPreconditionError,
    BEMServerAPIValidationError,
)
from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesBase:
    def test_api_client_resources_base(self):
        assert BaseResources.endpoint_base_uri == ""
        assert BaseResources.disabled_endpoints == []
        assert BaseResources.client_entrypoint is None

    def test_api_client_resources_base_verify_disabled(self):
        res = BaseResources(None)
        assert hasattr(res, "getall")

        assert "getall" not in res.disabled_endpoints
        with not_raises(NotImplementedError):
            res._verify_disabled("getall")

        res.disabled_endpoints = ["getall"]
        assert "getall" in res.disabled_endpoints
        with pytest.raises(NotImplementedError):
            res._verify_disabled("getall")

        assert not hasattr(res, "endpoint_name_that_does_not_exist")
        with pytest.raises(ValueError):
            res._verify_disabled("endpoint_name_that_does_not_exist")

    def test_api_client_resources_base_endpoint_uri_by_id(self):
        res = BaseResources(None)

        assert res.enpoint_uri_by_id(42) == "42"
        res.endpoint_base_uri = "/api/"
        assert res.enpoint_uri_by_id(42) == "/api/42"

    def test_api_client_resources_base_fake_endpoints(self, mock_request):
        res = BaseResources(mock_request)
        res.endpoint_base_uri = "/fake/"

        with pytest.raises(BEMServerAPIAuthenticationError):
            res.getall()

        resp = res.getall()
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_fake_list"
        assert resp.data == [
            {
                "id": 0,
                "name": "Fake #1",
            },
            {
                "id": 1,
                "name": "Fake #2",
            },
            {
                "id": 2,
                "name": "Fake #3",
            },
        ]

        with pytest.raises(BEMServerAPINotModified):
            res.getall(etag="etag_fake_list")

        resp = res.getone(0)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_fake_0"
        assert resp.data == {
            "id": 0,
            "name": "Fake #1",
        }

        with pytest.raises(BEMServerAPIValidationError) as excinfo:
            res.create({})
        assert "name" in excinfo.value.errors
        assert excinfo.value.errors["name"] == ["Missing data for required field."]

        with pytest.raises(BEMServerAPIValidationError) as excinfo:
            res.create(
                {
                    "name": "Fake #1",
                },
            )
        assert "name" in excinfo.value.errors
        assert excinfo.value.errors["name"] == ["Must be unique."]

        resp = res.create(
            {
                "name": "Fake #4",
            },
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 201
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_fake_3"
        assert resp.data == {
            "id": 3,
            "name": "Fake #4",
        }

        with pytest.raises(BEMServerAPIPreconditionError):
            res.update(
                0,
                {
                    "name": "Fake #1 updated",
                },
                etag=None,
            )

        with pytest.raises(BEMServerAPIPreconditionError):
            res.update(
                0,
                {
                    "name": "Fake #1 updated",
                },
                etag="bad_etag",
            )

        resp = res.update(
            0,
            {
                "name": "Fake #1 updated",
            },
            etag="etag_fake_0",
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_fake_0"
        assert resp.data == {
            "id": 0,
            "name": "Fake #1 updated",
        }

        resp = res.delete(0, etag="etag_fake_0")
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 204
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == ""
        assert resp.data == {}

        with pytest.raises(BEMServerAPINotFoundError):
            res.getone(0)

        with pytest.raises(BEMServerAPIAuthorizationError):
            res.getone(42)

        with pytest.raises(BEMServerAPIInternalError) as excinfo:
            res.getone(999)
        assert excinfo.value.status_code == 400

        with pytest.raises(BEMServerAPIInternalError) as excinfo:
            res.getone(666)
        assert excinfo.value.status_code == 500

        resp = res.getone("notjson")
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert not resp.is_json
        assert resp.pagination == {}
        assert resp.etag == ""
        assert resp.data == b"Hello!"

        with pytest.raises(BEMServerAPIInternalError):
            res.getone("timeout")
