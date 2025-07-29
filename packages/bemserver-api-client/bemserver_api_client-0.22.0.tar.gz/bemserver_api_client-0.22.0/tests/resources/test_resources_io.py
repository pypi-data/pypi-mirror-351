"""BEMServer API client IO resources tests"""

import io

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.io import IOResources
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesIO:
    def test_api_client_resources_io(self):
        assert issubclass(IOResources, BaseResources)
        assert IOResources.endpoint_base_uri == "/io/"
        assert IOResources.disabled_endpoints == [
            "getall",
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert IOResources.client_entrypoint == "io"
        assert hasattr(IOResources, "upload_timeseries_csv")
        assert hasattr(IOResources, "upload_sites_csv")

    def test_api_client_resources_io_endpoints(self, mock_request):
        io_res = IOResources(mock_request)

        timeseries_csv = (
            "Name,Description,Unit,Campaign scope,Site,Building,"
            "Storey,Space,Zone,Min,Max\n"
            "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,Site 1,Building 1,"
            "Storey 1,Space 1,Zone 1,-10,60\n"
            "Space_2_Temp,Temperature,°C,Campaign 1 - Scope 1,Site 1,Building 1,"
            "Storey 1,Space 1,Zone 1,-10,60\n"
        )
        resp = io_res.upload_timeseries_csv(
            0,
            {
                "timeseries_csv": io.BytesIO(timeseries_csv.encode()),
            },
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 201

        sites_csv = (
            "Name,Description,IFC_ID,Area\n"
            "Site 1,Great site 1,abcdefghijklmnopqrtsuv,1000\n"
            "Site 2,Great site 2,,2000\n"
        )
        resp = io_res.upload_sites_csv(
            0,
            {
                "sites_csv": io.BytesIO(sites_csv.encode()),
                "buildings_csv": None,
                "zones_csv": io.BytesIO(),
            },
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 201
