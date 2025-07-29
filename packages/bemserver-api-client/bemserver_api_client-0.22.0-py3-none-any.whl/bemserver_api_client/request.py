"""BEMServer API client request"""

import json
import logging
import os
from copy import deepcopy

import requests
import requests.exceptions as req_exc

from .authentication import BearerTokenAuth
from .enums import DataFormat
from .exceptions import (
    BEMServerAPIAuthenticationError,
    BEMServerAPIClientValueError,
    BEMServerAPIInternalError,
)
from .response import BEMServerApiClientResponse


class BEMServerApiClientRequest:
    """API client requester"""

    _ETAG_HEADER_BY_HTTP_METHOD = {
        "GET": "If-None-Match",
        "PUT": "If-Match",
        "DELETE": "If-Match",
    }

    def __init__(self, base_uri, authentication_method, *, logger=None):
        self.base_uri = base_uri

        self._logger = logger or logging.getLogger(__name__)
        self._session = requests.Session()
        self.set_authentication_method(authentication_method)

    @property
    def _is_bearer_token_auth(self):
        return isinstance(self._session.auth, BearerTokenAuth)

    @property
    def is_authentication_refreshing(self):
        return self._is_bearer_token_auth and self._session.auth.do_refresh

    @is_authentication_refreshing.setter
    def is_authentication_refreshing(self, value):
        # In token based authentication mode...
        if self._is_bearer_token_auth:
            # ...ensure that the refresh token will be used for this request.
            self._session.auth.do_refresh = value

    def _build_uri(self, endpoint_uri):
        return f"{self.base_uri}{endpoint_uri}"

    def _prepare_dataformat_header(self, http_method, format):
        """

        :raises TypeError: when format is None or not an enum type
        :raises BEMServerAPIClientValueError: when format is not in DataFormat enum
        """
        if format not in DataFormat._value2member_map_.values():
            raise BEMServerAPIClientValueError(f"Invalid data format: {format}")
        dataformat_header = {}
        if http_method.upper() == "GET":
            dataformat_header = {"Accept": format.value}
        elif http_method.upper() in ["POST", "PUT"]:
            dataformat_header = {"Content-Type": format.value}
        return dataformat_header

    def _prepare_etag_header(self, http_method, etag):
        etag_header = {}
        if etag is not None:
            try:
                etag_header = {
                    self._ETAG_HEADER_BY_HTTP_METHOD[http_method.upper()]: etag
                }
            except KeyError:
                pass
        return etag_header

    def _execute(self, http_method, endpoint, *, etag=None, **kwargs):
        try_refresh = kwargs.pop("try_refresh", True)
        _orig_kwargs = deepcopy(kwargs)

        full_endpoint_uri = self._build_uri(endpoint)
        headers = {
            **kwargs.pop("headers", {}),
            **self._prepare_etag_header(http_method, etag),
        }
        self._logger.debug(f"{http_method} {full_endpoint_uri}")
        try:
            raw_resp = self._session.request(
                http_method, full_endpoint_uri, headers=headers, **kwargs
            )
        except req_exc.RequestException as exc:
            self._logger.error(
                f"Unexpected error while requesting {full_endpoint_uri}: {exc}"
            )
            raise BEMServerAPIInternalError from exc

        try:
            return BEMServerApiClientResponse(raw_resp)
        except BEMServerAPIAuthenticationError as exc:
            # Catch 401 response to check if authentication mode is token based,
            #  current access token has expired and access token refresh is wanted.
            if (
                self._is_bearer_token_auth
                and exc.code == "expired_token"
                and try_refresh
            ):
                # Call the refresh tokens process (an error will be raised if it fails).
                self._session.auth.refresh_tokens_callback()
                # At this point refresh is ok, so just replay the request.
                return self._execute(
                    http_method, endpoint, etag=etag, try_refresh=False, **_orig_kwargs
                )
            else:
                # Authentication mode not token based or refresh not wanted/needed,
                #  raise initial authentication error.
                raise exc

    @staticmethod
    def _exclude_empty_files(files):
        """

        :param dict files:
            key is the upload field name (csv_file, timeseries_csv or sites_csv...)
            value is a file stream (tempfile.SpooledTemporaryFile)
        """
        not_empty_files = {}
        for k, v in files.items():
            if v is not None and v.seek(0, os.SEEK_END) > 0:
                v.seek(0, os.SEEK_SET)
                not_empty_files[k] = v
        return not_empty_files

    def set_authentication_method(self, authentication_method):
        self._session.auth = authentication_method

    def getall(self, endpoint, *, etag=None, **kwargs):
        return self._execute("GET", endpoint, etag=etag, **kwargs)

    def getone(self, endpoint, *, etag=None):
        return self._execute("GET", endpoint, etag=etag)

    def create(self, endpoint, payload):
        return self._execute("POST", endpoint, json=payload)

    def update(self, endpoint, payload, etag):
        return self._execute("PUT", endpoint, json=payload, etag=etag)

    def delete(self, endpoint, etag):
        return self._execute("DELETE", endpoint, etag=etag)

    def upload_files(self, endpoint, files, **kwargs):
        """Upload files.

        :param dict files:
            key is the upload field name (csv_file, timeseries_csv or sites_csv...)
            value is a file stream (tempfile.SpooledTemporaryFile)
        """
        not_empty_files = self._exclude_empty_files(files)
        return self._execute("POST", endpoint, files=not_empty_files, **kwargs)

    def upload_data(self, endpoint, data, *, format=DataFormat.json, **kwargs):
        """Upload data from specified format.

        :param bytes|dict data: data to upload (bytes for CSV format, dict for JSON)
        :param DataFormat format: (optional, default JSON)
            data format, either CSV or JSON
        """
        http_method = "POST"
        kwargs["headers"] = {
            **kwargs.pop("headers", {}),
            **self._prepare_dataformat_header(http_method, format),
        }
        if format == DataFormat.json:
            data = json.dumps(data)
        return self._execute(http_method, endpoint, data=data, **kwargs)

    def download(self, endpoint, *, format=DataFormat.json, **kwargs):
        """Download data in specified format.

        :param DataFormat format: (optional, default JSON)
            data format, either CSV or JSON
        """
        http_method = "GET"
        kwargs["headers"] = {
            **kwargs.pop("headers", {}),
            **self._prepare_dataformat_header(http_method, format),
        }
        return self._execute(http_method, endpoint, **kwargs)
