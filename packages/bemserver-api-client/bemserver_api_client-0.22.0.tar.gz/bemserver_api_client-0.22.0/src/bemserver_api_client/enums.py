"""BEMServer API client enums"""

import enum


class DataFormat(enum.Enum):
    csv = "text/csv"
    json = "application/json"


class Aggregation(enum.Enum):
    avg = "avg"
    sum = "sum"
    min = "min"
    max = "max"
    count = "count"


class BucketWidthUnit(enum.Enum):
    second = "second"
    minute = "minute"
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class EventLevel(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuralElement(enum.Enum):
    site = "site"
    building = "building"
    storey = "storey"
    space = "space"
    zone = "zone"


class StructuralElementPropertyValueType(enum.Enum):
    integer = "integer"
    float = "float"
    boolean = "boolean"
    string = "string"


class WeatherParameter(enum.Enum):
    AIR_TEMPERATURE = "Air temperature"
    DEWPOINT_TEMPERATURE = "Dewpoint temperature"
    WETBULB_TEMPERATURE = "Wetbulb temperature"
    WIND_SPEED = "Wind speed"
    WIND_DIRECTION = "Wind direction"
    SURFACE_SOLAR_RADIATION = "Surface solar radiation"
    SURFACE_DIRECT_SOLAR_RADIATION = "Surface direct solar radiation"
    SURFACE_DIFFUSE_SOLAR_RADIATION = "Surface diffuse solar radiation"
    DIRECT_NORMAL_SOLAR_RADIATION = "Direct normal solar radiation"
    RELATIVE_HUMIDITY = "Relative humidity"
    SURFACE_PRESSURE = "Surface pressure"
    TOTAL_PRECIPITATION = "Total precipitation"


class DegreeDaysPeriod(enum.Enum):
    day = "day"
    month = "month"
    year = "year"


class DegreeDaysType(enum.Enum):
    heating = "heating"
    cooling = "cooling"


class TaskOffsetUnit(enum.Enum):
    second = "second"
    minute = "minute"
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"
    year = "year"
