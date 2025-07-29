"""BEMServer API client response tests"""

import pytest

from bemserver_api_client.response import (
    BEMServerApiClientResponse,
    BEMServerAPIConflictError,
    BEMServerAPIInternalError,
    BEMServerAPIValidationError,
)


class TestAPIClientResponse:
    def test_api_client_response_tojson(self, mock_request):
        resp = mock_request.getone("/fake/0")
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert not resp.is_csv
        assert resp.toJSON() == {
            "status_code": resp.status_code,
            "data": resp.data,
            "etag": resp.etag,
            "pagination": resp.pagination,
        }

    @pytest.mark.parametrize(
        "mock_raw_response_internal_error",
        (
            {"status_code": 500},
            {"status_code": 400},
        ),
        indirect=True,
    )
    def test_api_client_response_error_internal(
        self,
        mock_raw_response_internal_error,
    ):
        raw_resp, status_code = mock_raw_response_internal_error
        with pytest.raises(BEMServerAPIInternalError) as excinfo:
            BEMServerApiClientResponse(raw_resp)
        assert excinfo.value.status_code == status_code

    @pytest.mark.parametrize(
        "mock_raw_response_409",
        (
            {"is_json": True},
            {"is_json": False},
        ),
        indirect=True,
    )
    def test_api_client_response_error_409(self, mock_raw_response_409):
        raw_resp, is_json = mock_raw_response_409
        with pytest.raises(BEMServerAPIConflictError) as excinfo:
            BEMServerApiClientResponse(raw_resp)
        if is_json:
            assert excinfo.value.message == "Unique constraint violation"
        else:
            assert excinfo.value.message == "Operation failed (409)!"

    @pytest.mark.parametrize(
        "mock_raw_response_422",
        (
            {"is_general": False},
            {"is_general": True},
            {"is_schema": True},
        ),
        indirect=True,
    )
    def test_api_client_response_error_422(self, mock_raw_response_422):
        raw_resp, is_general, is_schema = mock_raw_response_422
        with pytest.raises(BEMServerAPIValidationError) as excinfo:
            BEMServerApiClientResponse(raw_resp)
        if is_general:
            assert excinfo.value.errors == {
                "_general": ["Validation error message."],
            }
        elif is_schema:
            assert excinfo.value.errors == {
                "_general": ["Schema error."],
            }
        else:
            assert excinfo.value.errors == {
                "is_admin": ["Not a valid boolean."],
            }
