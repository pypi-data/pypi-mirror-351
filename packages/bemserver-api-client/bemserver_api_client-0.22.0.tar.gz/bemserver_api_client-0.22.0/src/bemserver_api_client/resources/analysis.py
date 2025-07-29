"""BEMServer API client resources

/analysis/ endpoints
"""

from ..enums import BucketWidthUnit, StructuralElement
from ..exceptions import BEMServerAPIClientValueError
from .base import BaseResources


class AnalysisResources(BaseResources):
    endpoint_base_uri = "/analysis/"
    disabled_endpoints = ["getall", "getone", "create", "update", "delete"]
    client_entrypoint = "analysis"

    def get_completeness(
        self,
        start_time,
        end_time,
        timeseries,
        data_state,
        bucket_width_value,
        bucket_width_unit,
        timezone="UTC",
        *,
        etag=None,
    ):
        if bucket_width_unit not in list(BucketWidthUnit):
            raise BEMServerAPIClientValueError(
                f"Invalid bucket width unit: {bucket_width_unit}"
            )

        endpoint = f"{self.endpoint_base_uri}completeness"
        q_params = {
            "start_time": start_time,
            "end_time": end_time,
            "timeseries": timeseries,
            "data_state": data_state,
            "bucket_width_value": bucket_width_value,
            "bucket_width_unit": bucket_width_unit.value,
            "timezone": timezone,
        }
        return self._req.getall(endpoint, etag=etag, params=q_params)

    def get_energy_consumption_breakdown(
        self,
        structural_element_type,
        structural_element_id,
        start_time,
        end_time,
        bucket_width_value,
        bucket_width_unit,
        timezone="UTC",
        unit="kWh",
        ratio_property=None,
        *,
        etag=None,
    ):
        # Only site and building structural element types are accepted.
        if structural_element_type not in [
            StructuralElement.site,
            StructuralElement.building,
        ]:
            raise BEMServerAPIClientValueError(
                f"Invalid structural element type: {structural_element_type}"
            )
        if bucket_width_unit not in list(BucketWidthUnit):
            raise BEMServerAPIClientValueError(
                f"Invalid bucket width unit: {bucket_width_unit}"
            )

        endpoint = (
            f"{self.endpoint_base_uri}energy_consumption/"
            f"{structural_element_type.value}/{structural_element_id}"
        )
        q_params = {
            "start_time": start_time,
            "end_time": end_time,
            "bucket_width_value": bucket_width_value,
            "bucket_width_unit": bucket_width_unit.value,
            "timezone": timezone,
            "unit": unit,
            "ratio_property": ratio_property,
        }
        return self._req.getall(endpoint, etag=etag, params=q_params)
