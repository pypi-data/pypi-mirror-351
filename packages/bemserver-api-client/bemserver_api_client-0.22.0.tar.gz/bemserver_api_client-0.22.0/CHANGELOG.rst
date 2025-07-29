=============
  Changelog
=============

0.22.0 (2025-05-27)
++++++++++++++++++

Features:

- Remove ``services`` endpoints
- Remove ``tasks`` and ``tasks_by_campaigns`` endpoints

Other changes:

- Require bemserver-api >=0.26.0 and <0.27.0

0.21.2 (2025-01-03)
++++++++++++++++++

Other changes:

- Require bemserver-api >=0.24.0 and <0.26.0

0.21.1 (2024-06-10)
++++++++++++++++++

Fixes:

- Require bemserver-api >=0.24.0 and <0.25.0

Other changes:

- Remove bad 0.21.0 release from PyPI
- Still require bemserver-api >=0.24.0 and <0.25.0
- Still require bemserver-core 0.18.0

0.21.0 (2024-06-10)
+++++++++++++++++++

Features:

- Add bearer token (JWT) authentication feature: ``auth.get_tokens`` and ``auth.refresh_tokens`` endpoints
- Dissociate 401 and 403 http status codes management by adding ``BEMServerAPIAuthorizationError`` error (403)

Other changes:

- Require bemserver-api >=0.24.0 and <0.25.0
- Require bemserver-core 0.18.0

Follows `API update 0.24.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0240-2024-06-06>`_

0.20.4 (2024-05-24)
+++++++++++++++++++

Features:

- Change licence to MIT
- Update README with documentation and example on BEMServerAPIClient usage

Fixes:

- JSON data encoding while using ``TimeseriesDataResources.upload`` and ``TimeseriesDataResources.upload_by_names`` endpoints

Other changes:

- Still require bemserver-api >=0.22.0 and <0.24.0
- Still require bemserver-core 0.17.1

0.20.3 (2024-02-13)
+++++++++++++++++++

API changes in version 0.23.0 do not affect client features.

Other changes:

- Require bemserver-api >=0.22.0 and <0.24.0
- Require bemserver-core 0.17.1

0.20.2 (2023-07-26)
+++++++++++++++++++

API changes in version 0.22.0 do not affect client features.

Other changes:

- Require bemserver-api >=0.22.0 and <0.23.0
- Require bemserver-core 0.16.2

Follows `API update 0.22.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0220-2023-07-25>`_

0.20.1 (2023-07-04)
+++++++++++++++++++

Features:

- Add ``StructuralElementPropertyValueType`` enum

0.20.0 (2023-06-13)
+++++++++++++++++++

API changes in version 0.21.0 do not affect client features.

Other changes:

- Require bemserver-api >=0.21.0 and <0.22.0
- Require bemserver-core 0.16.0

Follows `API update 0.21.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0210-2023-06-09>`_

0.19.1 (2023-05-23)
+++++++++++++++++++

Features:

- Add ``unit`` and ``ratio_property`` parameters on ``AnalysisResources.get_energy_consumption_breakdown`` endpoint

Other changes:

- Require bemserver-api >=0.20.1 and <0.21.0
- Require bemserver-core 0.15.1

Follows `API update 0.20.1 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0201-2023-05-22>`_

0.19.0 (2023-05-10)
+++++++++++++++++++

Features:

- Add download weather **forecast** data service resources

Other changes:

- Require bemserver-api >=0.20.0 and <0.21.0
- Require bemserver-core 0.15.0

Follows `API update 0.19.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0190-2023-05-05>`_ and `update 0.20.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0200-2023-05-05>`_

0.18.0 (2023-04-24)
+++++++++++++++++++

Features:

- Add ``TimeseriesDataResources.get_stats`` endpoint

Other changes:

- Require bemserver-api >=0.18.0 and <0.19.0
- Require bemserver-core 0.13.4

Follows `API update 0.18.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0180-2023-04-21>`_

0.17.2 (2023-04-20)
+++++++++++++++++++

Fixes:

- Fix ``SiteResources.get_degree_days`` endpoint

0.17.1 (2023-04-19)
+++++++++++++++++++

Features:

- Add ``SiteResources.download_weather_data`` endpoint
- Add ``SiteResources.get_degree_days`` endpoint
- Add ``DegreeDaysPeriod`` and ``DegreeDaysType`` enums

Other changes:

- Require bemserver-api >=0.17.3 and <0.18.0
- Require bemserver-core 0.13.2

Follows `API update 0.17.2 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0172-2023-04-18>`_ and `update 0.17.3 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0173-2023-04-18>`_

0.17.0 (2023-04-13)
+++++++++++++++++++

Features:

- Update ``timeseries_data.download*`` endpoints: add *convert_to* param
- Add download weather data service resources

Other changes:

- Require bemserver-api >=0.17.1 and <0.18.0
- Require bemserver-core 0.13.1

Follows `API update 0.17.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0170-2023-04-13>`_ and `update 0.17.1 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0171-2023-04-13>`_

0.16.0 (2023-03-30)
+++++++++++++++++++

Fixes:

- Fix MIME type for CSV data (``application/csv`` -> ``text/csv``)
- Fix header for upload requests (``Accept`` -> ``Content-Type``)

Other changes:

- Require bemserver-api >=0.16.0 and <0.17.0
- Still require bemserver-core 0.12.0

Follows `API update 0.16.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0160-2023-03-30>`_

0.15.0 (2023-03-14)
+++++++++++++++++++

Features:

- Update ``WeatherParameter`` enum (add ``SURFACE_DIRECT_SOLAR_RADIATION`` and ``SURFACE_DIFFUSE_SOLAR_RADIATION``)

Other changes:

- Require bemserver-api >=0.15.0 and <0.16.0
- Require bemserver-core 0.12.0

Follows `API update 0.15.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0150-2023-03-14>`_

0.14.0 (2023-03-06)
+++++++++++++++++++

Features:

- Add ``WeatherParameter`` enum

Other changes:

- Require bemserver-api >=0.14.0 and <0.15.0
- Require bemserver-core 0.11.1

Follows `API update 0.14.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0140-2023-03-06>`_

0.13.1 (2023-03-03)
+++++++++++++++++++

Fixes:

- Rollback ``TimeseriesDataResources.client_entrypoint`` value to "timesries_datastates" (to fix a regression since previous version)

Other changes:

- Require bemserver-api >=0.13.1 and <0.14.0

Follows `API update 0.13.1 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0131-2023-03-03>`_

0.13.0 (2023-03-03)
+++++++++++++++++++

Features:

- Rename ``EnergySourceResources`` to ``EnergyResources``
- Add ``energy_production_technologies`` endpoints (``EnergyProductionTechnologyResources``)
- Add ``energy_production_timeseries_by_*`` endpoints (``EnergyProductionTimseriesBySiteResources`` and ``EnergyProductionTimseriesByBuildingResources``)
- Add ``weather_timeseries_by_sites`` endpoints (``WeatherTimseriesBySiteResources``)

Fixes:

- Raise ``BEMServerAPIClientValueError`` when ``AnalysisResources.get_completeness()`` is called with an unsupported bucket width
- Raise ``BEMServerAPIClientValueError`` when ``AnalysisResources.get_energy_consumption_breakdown()`` is called with an unsupported structural element type (not site or building)
- Raise ``BEMServerAPIClientValueError`` when ``TimeseriesDataResources.download_aggregate()`` is called with an unsupported aggregation or bucket width
- Raise ``BEMServerAPIClientValueError`` when ``TimeseriesDataResources.download_aggregate_by_names()`` is called with an unsupported aggregation or bucket width

Other changes:

- Require bemserver-api >=0.13.0 and <0.14.0
- Require bemserver-core 0.11.0

Follows `API update 0.13.0 <https://github.com/BEMServer/bemserver-api/blob/master/CHANGELOG.rst#0130-2023-03-01>`_

0.12.1 (2023-03-01)
+++++++++++++++++++

Fixes:

- Improve 409 client error processing (raises BEMServerAPIConflictError, with message)

Other changes:

- Require bemserver-api >=0.12.1 and <0.13.0

0.12.0 (2023-02-28)
+++++++++++++++++++

Other changes:

- Require bemserver-api >=0.12.0 and <0.13.0
- Require bemserver-core 0.10.1

0.11.1 (2023-02-13)
+++++++++++++++++++

Other changes:

- Require bemserver-api >=0.11.1 and <0.12.0

0.11.0 (2023-02-09)
+++++++++++++++++++

Features:

- Add ``StructuralElement`` enum
- Change ``AnalysisResources.get_energy_consumption_breakdown()``'s ``structural_element_type`` parameter type to use ``StructuralElement`` enum

Other changes:

- Require bemserver-api >=0.11.0 and <0.12.0
- Require bemserver-core 0.9.1

0.10.2 (2023-02-07)
+++++++++++++++++++

Other changes:

- Require bemserver-api >=0.10.3 and <0.11.0

0.10.1 (2023-02-01)
+++++++++++++++++++

Features:

- Update notifications resources:

  - add *campaign_id* filter on list endpoint
  - add ``count_by_campaign`` endpoint
  - add ``mark_all_as_read`` endpoint

Other changes:

- Require bemserver-api >=0.10.2 and <0.11.0
- Require bemserver-core 0.8.1

0.10.0 (2023-01-23)
+++++++++++++++++++

Features:

- Add check outliers data service resources

Other changes:

- Require bemserver-api >=0.10.0 and <0.11.0
- Require bemserver-core 0.8.0

0.9.0 (2023-01-12)
++++++++++++++++++

Client not really affected by API changes in version 0.9.0 (some ETags removed...).

Other changes:

- Require bemserver-api >=0.9.0 and <0.10.0
- Require bemserver-core 0.7.0

0.8.0 (2023-01-12)
++++++++++++++++++

Features:

- Remove timeseries get by sites/buildings/storeys/spaces/zones and by events resources
- Remove get events by sites/buildings/storeys/spaces/zones resources

Other changes:

- Require bemserver-api >=0.8.0 and <0.9.0
- Require bemserver-core 0.7.0

0.7.0 (2023-01-09)
++++++++++++++++++

Features:

- Add event categories by users resources
- Add notifications resources

Other changes:

- Require bemserver-api >=0.7.0 and <0.8.0
- Require bemserver-core 0.6.0

0.6.0 (2023-01-09)
++++++++++++++++++

Features:

- Add get events by sites/buildings/storeys/spaces/zones resources
- Add timeseries get by sites/buildings/storeys/spaces/zones and events resources

Other changes:

- Require bemserver-api >=0.6.0 and <0.7.0
- Require bemserver-core 0.5.0

0.5.2 (2023-01-09)
++++++++++++++++++

Fixes:

- Require bemserver-api still >=0.5.0 and <0.6.0

Other changes:

- Remove unusable 0.5.1 release from PyPI

0.5.1 (2023-01-06)
++++++++++++++++++

Fixes:

- Remove obsolete event_levels resources

Other changes:

- Support Python 3.11

0.5.0 (2022-12-15)
++++++++++++++++++

Features:

- Event API updates on query args:

  - replace *level_id* with ``EventLevel`` enum
  - add *level_min* and *in_source*

- Timeseries API: add *event_id* query arg

Other changes:

- Require bemserver-api >=0.5.0 and <0.6.0
- Require bemserver-core 0.4.0

0.4.0 (2022-12-15)
++++++++++++++++++

Features:

- Add events by sites/buildings/storeys/spaces/zones resources
- Remove update on timeseries_by_events resources

Other changes:

- Require bemserver-api >=0.4.0 and <0.5.0
- Require bemserver-core 0.3.0

0.3.0 (2022-12-07)
++++++++++++++++++

Features:

- Add Events (levels, categories...) resources
- Add check missing service resources

Other changes:

- Require bemserver-api >=0.3.0 and <0.4.0
- Require bemserver-core 0.2.1

0.2.0 (2022-11-30)
++++++++++++++++++

Features:

- Timeseries data upload/download in JSON format
- Add ``DataFormat``, ``Aggregation`` and ``BucketWidthUnit`` enums

Other changes:

- Require bemserver-api >=0.2.0 and <0.3.0
- Require bemserver-core 0.2.0

0.1.0 (2022-11-22)
++++++++++++++++++

Features:

- Authentication (HTTP BASIC)
- Check required BEMServer API version
- Implement all BEMServer API endpoints
- Manage BEMServer API responses (errors, ETag, pagination...)

Other changes:

- Require bemserver-api >=0.1.0 and <0.2.0
- Require bemserver-core 0.1.0
