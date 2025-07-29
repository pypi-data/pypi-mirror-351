"""BEMServer API client enums tests"""

from bemserver_api_client.enums import (
    Aggregation,
    BucketWidthUnit,
    DataFormat,
    DegreeDaysPeriod,
    DegreeDaysType,
    EventLevel,
    StructuralElement,
    StructuralElementPropertyValueType,
    TaskOffsetUnit,
    WeatherParameter,
)


class TestAPIClientEnums:
    def test_api_client_enums_data_format(self):
        assert len(list(DataFormat)) == 2
        assert DataFormat.csv.value == "text/csv"
        assert DataFormat.json.value == "application/json"

    def test_api_client_enums_aggregation(self):
        assert len(list(Aggregation)) == 5
        assert Aggregation.avg.value == "avg"
        assert Aggregation.sum.value == "sum"
        assert Aggregation.min.value == "min"
        assert Aggregation.max.value == "max"
        assert Aggregation.count.value == "count"

    def test_api_client_enums_bucket_width_unit(self):
        assert len(list(BucketWidthUnit)) == 7
        assert BucketWidthUnit.second.value == "second"
        assert BucketWidthUnit.minute.value == "minute"
        assert BucketWidthUnit.hour.value == "hour"
        assert BucketWidthUnit.day.value == "day"
        assert BucketWidthUnit.week.value == "week"
        assert BucketWidthUnit.month.value == "month"
        assert BucketWidthUnit.year.value == "year"

    def test_api_client_enums_event_level(self):
        assert len(list(EventLevel)) == 5
        assert EventLevel.DEBUG.value == "DEBUG"
        assert EventLevel.INFO.value == "INFO"
        assert EventLevel.WARNING.value == "WARNING"
        assert EventLevel.ERROR.value == "ERROR"
        assert EventLevel.CRITICAL.value == "CRITICAL"

    def test_api_client_enums_structural_element(self):
        assert len(list(StructuralElement)) == 5
        assert StructuralElement.site.value == "site"
        assert StructuralElement.building.value == "building"
        assert StructuralElement.storey.value == "storey"
        assert StructuralElement.space.value == "space"
        assert StructuralElement.zone.value == "zone"

    def test_api_client_enums_structural_element_property_type(self):
        assert len(list(StructuralElementPropertyValueType)) == 4
        assert StructuralElementPropertyValueType.integer.value == "integer"
        assert StructuralElementPropertyValueType.float.value == "float"
        assert StructuralElementPropertyValueType.boolean.value == "boolean"
        assert StructuralElementPropertyValueType.string.value == "string"

    def test_api_client_enums_weather_parameter(self):
        assert len(list(WeatherParameter)) == 12
        assert WeatherParameter.AIR_TEMPERATURE.value == "Air temperature"
        assert WeatherParameter.DEWPOINT_TEMPERATURE.value == "Dewpoint temperature"
        assert WeatherParameter.WETBULB_TEMPERATURE.value == "Wetbulb temperature"
        assert WeatherParameter.WIND_SPEED.value == "Wind speed"
        assert WeatherParameter.WIND_DIRECTION.value == "Wind direction"
        assert WeatherParameter.SURFACE_SOLAR_RADIATION.value == (
            "Surface solar radiation"
        )
        assert WeatherParameter.SURFACE_DIRECT_SOLAR_RADIATION.value == (
            "Surface direct solar radiation"
        )
        assert WeatherParameter.SURFACE_DIFFUSE_SOLAR_RADIATION.value == (
            "Surface diffuse solar radiation"
        )
        assert WeatherParameter.DIRECT_NORMAL_SOLAR_RADIATION.value == (
            "Direct normal solar radiation"
        )
        assert WeatherParameter.RELATIVE_HUMIDITY.value == "Relative humidity"
        assert WeatherParameter.SURFACE_PRESSURE.value == "Surface pressure"
        assert WeatherParameter.TOTAL_PRECIPITATION.value == "Total precipitation"

    def test_api_client_enums_degree_days_period(self):
        assert len(list(DegreeDaysPeriod)) == 3
        assert DegreeDaysPeriod.day.value == "day"
        assert DegreeDaysPeriod.month.value == "month"
        assert DegreeDaysPeriod.year.value == "year"

    def test_api_client_enums_degree_days_type(self):
        assert len(list(DegreeDaysType)) == 2
        assert DegreeDaysType.heating.value == "heating"
        assert DegreeDaysType.cooling.value == "cooling"

    def test_api_client_enums_task_offset_unit(self):
        assert len(list(TaskOffsetUnit)) == 7
        assert TaskOffsetUnit.second.value == "second"
        assert TaskOffsetUnit.minute.value == "minute"
        assert TaskOffsetUnit.hour.value == "hour"
        assert TaskOffsetUnit.day.value == "day"
        assert TaskOffsetUnit.week.value == "week"
        assert TaskOffsetUnit.month.value == "month"
        assert TaskOffsetUnit.year.value == "year"
