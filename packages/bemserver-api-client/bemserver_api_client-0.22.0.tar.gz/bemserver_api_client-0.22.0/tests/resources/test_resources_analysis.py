"""BEMServer API client analysis resources tests"""

import pytest

from tests.conftest import FakeEnum

from bemserver_api_client.enums import BucketWidthUnit, StructuralElement
from bemserver_api_client.exceptions import BEMServerAPIClientValueError
from bemserver_api_client.resources.analysis import AnalysisResources
from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesAnalysis:
    def test_api_client_resources_analysis(self):
        assert issubclass(AnalysisResources, BaseResources)
        assert AnalysisResources.endpoint_base_uri == "/analysis/"
        assert AnalysisResources.disabled_endpoints == [
            "getall",
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert AnalysisResources.client_entrypoint == "analysis"
        assert hasattr(AnalysisResources, "get_completeness")
        assert hasattr(AnalysisResources, "get_energy_consumption_breakdown")

    def test_api_client_resources_analysis_endpoints(self, mock_request):
        analysis_res = AnalysisResources(mock_request)
        # Get completeness
        resp = analysis_res.get_completeness(
            start_time="2020-01-01T00:00:00+00:00",
            end_time="2020-02-01T00:00:00+00:00",
            timeseries=[1, 2],
            data_state=1,
            bucket_width_value=1,
            bucket_width_unit=BucketWidthUnit.week,
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_analysis_completeness"
        assert resp.data == {
            "timeseries": {
                "1": {
                    "avg_count": 893.4,
                    "avg_ratio": 1.0007539682539683,
                    "count": [721, 1008, 1009, 1008, 721],
                    "expected_count": [720, 1008, 1008, 1008, 720],
                    "interval": 600,
                    "name": "AirTempAngF1Off",
                    "ratio": [1, 1, 1, 1, 1],
                    "total_count": 4467,
                    "undefined_interval": False,
                },
                "2": {
                    "avg_count": 893.4,
                    "avg_ratio": 1.0007539682539683,
                    "count": [721, 1008, 1009, 1008, 721],
                    "expected_count": [720, 1008, 1008, 1008, 720],
                    "interval": 600,
                    "name": "AirTempAngF2Off",
                    "ratio": [1, 1, 1, 1, 1],
                    "total_count": 4467,
                    "undefined_interval": False,
                },
            },
            "timestamps": [
                "2019-12-30T00:00:00+00:00",
                "2020-01-06T00:00:00+00:00",
                "2020-01-13T00:00:00+00:00",
                "2020-01-20T00:00:00+00:00",
                "2020-01-27T00:00:00+00:00",
            ],
        }

        # Get energy consumption breakdown
        resp = analysis_res.get_energy_consumption_breakdown(
            StructuralElement.site,
            1,
            start_time="2020-01-01T00:00:00+00:00",
            end_time="2020-02-01T00:00:00+00:00",
            bucket_width_value=1,
            bucket_width_unit=BucketWidthUnit.week,
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_analysis_energy_cons_site"
        assert resp.data == {
            "energy": {
                "all": {
                    "all": [0, 0, 0, 0, 0],
                    "appliances": [0, 0, 0, 0, 0],
                    "lighting": [0, 0, 0, 0, 0],
                    "ventilation": [0, 0, 0, 0, 0],
                },
                "electricity": {
                    "all": [0, 0, 0, 0, 0],
                    "heating": [0, 0, 0, 0, 0],
                },
            },
            "timestamps": [
                "2019-12-30T00:00:00+00:00",
                "2020-01-06T00:00:00+00:00",
                "2020-01-13T00:00:00+00:00",
                "2020-01-20T00:00:00+00:00",
                "2020-01-27T00:00:00+00:00",
            ],
        }
        # Get energy consumption breakdown, with kWh unit and Area ratio
        resp = analysis_res.get_energy_consumption_breakdown(
            StructuralElement.site,
            1,
            start_time="2020-01-01T00:00:00+00:00",
            end_time="2020-02-01T00:00:00+00:00",
            bucket_width_value=1,
            bucket_width_unit=BucketWidthUnit.week,
            unit="kWh",
            ratio_property="Area",
        )
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.pagination == {}
        assert resp.etag == "etag_analysis_energy_cons_site"
        assert resp.data == {
            "energy": {
                "all": {
                    "all": [0, 0, 0, 0, 0],
                    "appliances": [0, 0, 0, 0, 0],
                    "lighting": [0, 0, 0, 0, 0],
                    "ventilation": [0, 0, 0, 0, 0],
                },
                "electricity": {
                    "all": [0, 0, 0, 0, 0],
                    "heating": [0, 0, 0, 0, 0],
                },
            },
            "timestamps": [
                "2019-12-30T00:00:00+00:00",
                "2020-01-06T00:00:00+00:00",
                "2020-01-13T00:00:00+00:00",
                "2020-01-20T00:00:00+00:00",
                "2020-01-27T00:00:00+00:00",
            ],
        }

    def test_api_client_resources_analysis_endpoints_errors(self, mock_request):
        analysis_res = AnalysisResources(mock_request)

        for bad_bucket_width_unit in [None, "week", "other", 42, FakeEnum.b]:
            with pytest.raises(
                BEMServerAPIClientValueError,
                match=f"Invalid bucket width unit: {bad_bucket_width_unit}",
            ):
                analysis_res.get_completeness(
                    start_time="2020-01-01T00:00:00+00:00",
                    end_time="2020-02-01T00:00:00+00:00",
                    timeseries=[1, 2],
                    data_state=1,
                    bucket_width_value=1,
                    bucket_width_unit=bad_bucket_width_unit,
                )

        for bad_bucket_width_unit in [None, "week", "other", 42, FakeEnum.b]:
            with pytest.raises(
                BEMServerAPIClientValueError,
                match=f"Invalid bucket width unit: {bad_bucket_width_unit}",
            ):
                analysis_res.get_energy_consumption_breakdown(
                    StructuralElement.site,
                    1,
                    start_time="2020-01-01T00:00:00+00:00",
                    end_time="2020-02-01T00:00:00+00:00",
                    bucket_width_value=1,
                    bucket_width_unit=bad_bucket_width_unit,
                )

        for bad_structural_element_type in [
            None,
            "site",
            "other",
            42,
            FakeEnum.b,
            StructuralElement.storey,
            StructuralElement.space,
            StructuralElement.zone,
        ]:
            with pytest.raises(
                BEMServerAPIClientValueError,
                match=f"Invalid structural element type: {bad_structural_element_type}",
            ):
                analysis_res.get_energy_consumption_breakdown(
                    bad_structural_element_type,
                    1,
                    start_time="2020-01-01T00:00:00+00:00",
                    end_time="2020-02-01T00:00:00+00:00",
                    bucket_width_value=1,
                    bucket_width_unit=BucketWidthUnit.week,
                )
