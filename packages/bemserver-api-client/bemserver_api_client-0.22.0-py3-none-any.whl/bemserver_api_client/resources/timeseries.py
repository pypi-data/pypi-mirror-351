"""BEMServer API client resources

/timeseries/ endpoints
/timeseries_data_states/ endpoints
/timeseries_properties/ endpoints
/timeseries_property_data/ endpoints
/timeseries_data/ endpoints
/timeseries_by_sites/ endpoints
/timeseries_by_buildings/ endpoints
/timeseries_by_storeys/ endpoints
/timeseries_by_spaces/ endpoints
/timeseries_by_zones/ endpoints
/timeseries_by_events/ endpoints
"""

from ..enums import Aggregation, BucketWidthUnit, DataFormat
from ..exceptions import BEMServerAPIClientValueError
from .base import BaseResources


class TimeseriesResources(BaseResources):
    endpoint_base_uri = "/timeseries/"
    client_entrypoint = "timeseries"


class TimeseriesDataStateResources(BaseResources):
    endpoint_base_uri = "/timeseries_data_states/"
    client_entrypoint = "timeseries_datastates"


class TimeseriesPropertyResources(BaseResources):
    endpoint_base_uri = "/timeseries_properties/"
    client_entrypoint = "timeseries_properties"


class TimeseriesPropertyDataResources(BaseResources):
    endpoint_base_uri = "/timeseries_property_data/"
    client_entrypoint = "timeseries_property_data"


class TimeseriesDataResources(BaseResources):
    endpoint_base_uri = "/timeseries_data/"
    disabled_endpoints = ["getall", "getone", "create", "update"]
    client_entrypoint = "timeseries_data"

    def endpoint_uri_by_campaign(self, campaign_id):
        return f"{self.endpoint_base_uri}campaign/{str(campaign_id)}/"

    def get_stats(self, data_state, timeseries_ids, timezone="UTC"):
        return self._req._execute(
            "GET",
            f"{self.endpoint_base_uri}stats",
            params={
                "data_state": data_state,
                "timeseries": timeseries_ids,
                "timezone": timezone,
            },
        )

    def upload(self, data_state, data, format=DataFormat.json):
        """

        :param int data_state: timeseries data state id to feed
        :param bytes|dict data: data to upload (bytes for CSV format, dict for JSON)
        :param DataFormat format: (optional, default JSON)
            data format, either CSV or JSON
        """
        return self._req.upload_data(
            self.endpoint_base_uri,
            data,
            format=format,
            params={"data_state": data_state},
        )

    def upload_by_names(self, campaign_id, data_state, data, format=DataFormat.json):
        """

        :param int data_state: timeseries data state id to feed
        :param bytes|dict data: data to upload (bytes for CSV format, dict for JSON)
        :param DataFormat format: (optional, default JSON)
            data format, either CSV or JSON
        """
        return self._req.upload_data(
            self.endpoint_uri_by_campaign(campaign_id),
            data,
            format=format,
            params={"data_state": data_state},
        )

    def download(
        self,
        start_time,
        end_time,
        data_state,
        timeseries_ids,
        timezone="UTC",
        format=DataFormat.json,
        convert_to=None,
    ):
        return self._req.download(
            self.endpoint_base_uri,
            format=format,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "data_state": data_state,
                "timeseries": timeseries_ids,
                "timezone": timezone,
                "convert_to": convert_to,
            },
        )

    def download_by_names(
        self,
        campaign_id,
        start_time,
        end_time,
        data_state,
        timeseries_names,
        timezone="UTC",
        format=DataFormat.json,
        convert_to=None,
    ):
        return self._req.download(
            self.endpoint_uri_by_campaign(campaign_id),
            format=format,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "data_state": data_state,
                "timeseries": timeseries_names,
                "timezone": timezone,
                "convert_to": convert_to,
            },
        )

    def download_aggregate(
        self,
        start_time,
        end_time,
        data_state,
        timeseries_ids,
        timezone="UTC",
        aggregation=Aggregation.avg,
        bucket_width_value="1",
        bucket_width_unit=BucketWidthUnit.hour,
        format=DataFormat.json,
        convert_to=None,
    ):
        if aggregation not in list(Aggregation):
            raise BEMServerAPIClientValueError(f"Invalid aggregation: {aggregation}")
        if bucket_width_unit not in list(BucketWidthUnit):
            raise BEMServerAPIClientValueError(
                f"Invalid bucket width unit: {bucket_width_unit}"
            )

        return self._req.download(
            f"{self.endpoint_base_uri}aggregate",
            format=format,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "data_state": data_state,
                "timeseries": timeseries_ids,
                "timezone": timezone,
                "aggregation": aggregation.value,
                "bucket_width_value": bucket_width_value,
                "bucket_width_unit": bucket_width_unit.value,
                "convert_to": convert_to,
            },
        )

    def download_aggregate_by_names(
        self,
        campaign_id,
        start_time,
        end_time,
        data_state,
        timeseries_names,
        timezone="UTC",
        aggregation=Aggregation.avg,
        bucket_width_value="1",
        bucket_width_unit=BucketWidthUnit.hour,
        format=DataFormat.json,
        convert_to=None,
    ):
        if aggregation not in list(Aggregation):
            raise BEMServerAPIClientValueError(f"Invalid aggregation: {aggregation}")
        if bucket_width_unit not in list(BucketWidthUnit):
            raise BEMServerAPIClientValueError(
                f"Invalid bucket width unit: {bucket_width_unit}"
            )

        return self._req.download(
            f"{self.endpoint_uri_by_campaign(campaign_id)}aggregate",
            format=format,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "data_state": data_state,
                "timeseries": timeseries_names,
                "timezone": timezone,
                "aggregation": aggregation.value,
                "bucket_width_value": bucket_width_value,
                "bucket_width_unit": bucket_width_unit.value,
                "convert_to": convert_to,
            },
        )

    def delete(self, start_time, end_time, data_state, timeseries_ids):
        return self._req._execute(
            "DELETE",
            self.endpoint_base_uri,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "data_state": data_state,
                "timeseries": timeseries_ids,
            },
        )

    def delete_by_names(
        self,
        campaign_id,
        start_time,
        end_time,
        data_state,
        timeseries_names,
    ):
        return self._req._execute(
            "DELETE",
            self.endpoint_uri_by_campaign(campaign_id),
            params={
                "start_time": start_time,
                "end_time": end_time,
                "data_state": data_state,
                "timeseries": timeseries_names,
            },
        )


class TimeseriesBySiteResources(BaseResources):
    endpoint_base_uri = "/timeseries_by_sites/"
    disabled_endpoints = ["update"]
    client_entrypoint = "timeseries_by_sites"


class TimeseriesByBuildingResources(BaseResources):
    endpoint_base_uri = "/timeseries_by_buildings/"
    disabled_endpoints = ["update"]
    client_entrypoint = "timeseries_by_buildings"


class TimeseriesByStoreyResources(BaseResources):
    endpoint_base_uri = "/timeseries_by_storeys/"
    disabled_endpoints = ["update"]
    client_entrypoint = "timeseries_by_storeys"


class TimeseriesBySpaceResources(BaseResources):
    endpoint_base_uri = "/timeseries_by_spaces/"
    disabled_endpoints = ["update"]
    client_entrypoint = "timeseries_by_spaces"


class TimeseriesByZoneResources(BaseResources):
    endpoint_base_uri = "/timeseries_by_zones/"
    disabled_endpoints = ["update"]
    client_entrypoint = "timeseries_by_zones"


class TimeseriesByEventResources(BaseResources):
    endpoint_base_uri = "/timeseries_by_events/"
    disabled_endpoints = ["update"]
    client_entrypoint = "timeseries_by_events"
