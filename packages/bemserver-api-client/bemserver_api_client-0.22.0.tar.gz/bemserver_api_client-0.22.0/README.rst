========================
  BEMServer API client
========================

|img_pypi| |img_python| |img_build| |img_precommit| |img_codecov|

.. |img_pypi| image:: https://img.shields.io/pypi/v/bemserver-api-client.svg
    :target: https://pypi.org/project/bemserver-api-client/
    :alt: Latest version

.. |img_python| image:: https://img.shields.io/pypi/pyversions/bemserver-api-client.svg
    :target: https://pypi.org/project/bemserver-api-client/
    :alt: Python versions

.. |img_build| image:: https://github.com/BEMServer/bemserver-api-client/actions/workflows/build-release.yaml/badge.svg
    :target: https://github.com/bemserver/bemserver-api-client/actions?query=workflow%3Abuild
    :alt: Build status

.. |img_precommit| image:: https://results.pre-commit.ci/badge/github/bemserver/bemserver-api-client/main.svg
   :target: https://results.pre-commit.ci/latest/github/bemserver/bemserver-api-client/main
   :alt: pre-commit.ci status

.. |img_codecov| image:: https://codecov.io/gh/BEMServer/bemserver-api-client/branch/main/graph/badge.svg?token=FA5TO5HUKP
    :target: https://codecov.io/gh/bemserver/bemserver-api-client
    :alt: Code coverage


BEMServer is a free Building Energy Management software platform.

Its purpose is to store data collected in buildings and produce useful information such as performance indicators or alerts.


This package is a client for `BEMServer API <https://github.com/BEMServer/bemserver-api>`_, based on `requests <https://pypi.org/project/requests/>`_.


API client usage
================

.. code:: python3

    from bemserver_api_client import BEMServerApiClient

    # Get an instance of API client, setting the API host and the authentication method used for API requests.
    api_client = BEMServerApiClient(
        "localhost:5000",
        authentication_method=BEMServerApiClient.make_http_basic(
            "user@email.com", "password"
        ),
    )


Entry points
------------

API resources are accessible through dedicated entry points (python attributes) in API client instance.

For example, ``/sites/`` resources are requestable using the ``sites`` attribute but ``/energy_consumption_timeseries_by_sites/`` can be requested using ``energy_cons_ts_by_sites`` (which name is a little shorter than the original).

.. code:: python3

    # Get a list of all the sites available for the authenticated user.
    sites_resp = api_client.sites.getall()


Most of the API client entry points has **common functions** (``CF``) to request the API endpoints (actions on resources):

* ``getall`` to *GET* a list of resources
* ``getone`` to *GET* one specific resource (by its ID)
* ``create`` to *POST* a new resource
* ``update`` to *UPDATE* one specific resource
* ``delete`` to *DELETE* one specific resource


    Pay attention that, as described in the *API documentation*, some actions are not available on certain API resources (see ``/timeseries_data/``).
    Other API resources have additional actions, like on ``sites`` where it is possible to call ``get_degree_days`` and ``download_weather_data`` functions.

The tables below shows the correspondance between API endpoint uris and API client entry points with their available functions.

    ``CF`` mentions that the entry point described implements all **common functions** (getall, getone, create, update, delete).
    ``CF`` - ``update`` means that all common functions are implemented less the ``update`` one.


Authentication
~~~~~~~~~~~~~~

+---------------+-------------------------+---------------------------------------+
| API resources | API client entry points |    API client entry point actions     |
+===============+=========================+=======================================+
| /auth/        | auth                    | ``get_tokens``, ``refresh_tokens``    |
+---------------+-------------------------+---------------------------------------+


General
~~~~~~~

+-------------------------------------+-----------------------------------+--------------------------------------------------+
|            API resources            |      API client entry points      |          API client entry point actions          |
+=====================================+===================================+==================================================+
| /about/                             | about                             | ``getall``                                       |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /users/                             | users                             | ``CF``, ``set_admin``, ``set_active``            |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /users_by_user_groups/              | user_by_user_groups               | ``CF`` - ``update``                              |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /user_groups/                       | user_groups                       | ``CF``                                           |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /user_groups_by_campaigns/          | user_groups_by_campaigns          | ``CF`` - ``update``                              |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /user_groups_by_campaign_scopes/    | user_groups_by_campaign_scopes    | ``CF`` - ``update``                              |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /campaigns/                         | campaigns                         | ``CF``                                           |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /campaign_scopes/                   | campaign_scopes                   | ``CF``                                           |
+-------------------------------------+-----------------------------------+--------------------------------------------------+
| /io/                                | io                                | ``upload_sites_csv``, ``upload_timeseries_csv``  |
+-------------------------------------+-----------------------------------+--------------------------------------------------+


Structural elements
~~~~~~~~~~~~~~~~~~~

+-------------------------------------+-----------------------------------+--------------------------------------------------------+
|            API resources            |      API client entry points      |             API client entry point actions             |
+=====================================+===================================+========================================================+
| /sites/                             | sites                             | ``CF``, ``download_weather_data``, ``get_degree_days`` |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /buildings/                         | buildings                         | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /storeys/                           | storeys                           | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /spaces/                            | spaces                            | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /zones/                             | zones                             | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /structural_element_properties/     | structural_element_properties     | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /site_properties/                   | site_properties                   | ``CF`` - ``update``                                    |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /site_property_data/                | site_property_data                | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /building_properties/               | building_properties               | ``CF`` - ``update``                                    |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /building_property_data/            | building_property_data            | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /storey_properties/                 | storey_properties                 | ``CF`` - ``update``                                    |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /storey_property_data/              | storey_property_data              | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /space_properties/                  | space_properties                  | ``CF`` - ``update``                                    |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /space_property_data/               | space_property_data               | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /zone_properties/                   | zone_properties                   | ``CF`` - ``update``                                    |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+
| /zone_property_data/                | zone_property_data                | ``CF``                                                 |
+-------------------------------------+-----------------------------------+--------------------------------------------------------+


Timeseries
~~~~~~~~~~

+----------------------------------+-----------------------------+----------------------------------+
|          API resources           |   API client entry points   |  API client entry point actions  |
+==================================+=============================+==================================+
| /timeseries/                     | timeseries                  | ``CF``                           |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_properties/          | timeseries_properties       | ``CF``                           |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_property_data/       | timeseries_property_data    | ``CF``                           |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_by_sites/            | timeseries_by_sites         | ``CF`` - ``update``              |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_by_buildings/        | timeseries_by_buildings     | ``CF`` - ``update``              |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_by_storeys/          | timeseries_by_storeys       | ``CF`` - ``update``              |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_by_spaces/           | timeseries_by_spaces        | ``CF`` - ``update``              |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_by_zones/            | timeseries_by_zones         | ``CF`` - ``update``              |
+----------------------------------+-----------------------------+----------------------------------+
| /timeseries_by_events/           | timeseries_by_events        | ``CF`` - ``update``              |
+----------------------------------+-----------------------------+----------------------------------+
| /weather_timeseries_by_sites/    | weather_ts_by_sites         | ``CF``                           |
+----------------------------------+-----------------------------+----------------------------------+


Timeseries data
~~~~~~~~~~~~~~~

+-----------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|        API resources        |  API client entry points |                                                                   API client entry point actions                                                                              |
+=============================+==========================+===============================================================================================================================================================================+
| /timeseries_data_states/    | timeseries_datastates    | ``CF``                                                                                                                                                                        |
+-----------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| /timeseries_data/           | timeseries_data          | ``delete``, ``delete_by_names``, ``get_stats``, ``upload``, ``upload_by_names``, ``download``, ``download_by_names``, ``download_aggregate``, ``download_aggregate_by_names`` |
+-----------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Analysis
~~~~~~~~

+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
|                  API resources                  |    API client entry points     |                API client entry point actions                 |
+=================================================+================================+===============================================================+
| /analysis/                                      | analysis                       | ``get_completeness``, ``get_energy_consumption_breakdown``    |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energies/                                      | energies                       | ``getall``                                                    |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energy_end_uses/                               | energy_end_uses                | ``getall``                                                    |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energy_consumption_timeseries_by_sites/        | energy_cons_ts_by_sites        | ``CF``                                                        |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energy_consumption_timeseries_by_buildings/    | energy_cons_ts_by_buildings    | ``CF``                                                        |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energy_production_technologies/                | energy_prod_technologies       | ``getall``                                                    |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energy_production_timeseries_by_sites/         | energy_prod_ts_by_sites        | ``CF``                                                        |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+
| /energy_production_timeseries_by_buildings/     | energy_prod_ts_by_buildings    | ``CF``                                                        |
+-------------------------------------------------+--------------------------------+---------------------------------------------------------------+


Events and notifications
~~~~~~~~~~~~~~~~~~~~~~~~

+--------------------------------+------------------------------+--------------------------------------------------------+
|         API resources          |   API client entry points    |             API client entry point actions             |
+================================+==============================+========================================================+
| /events/                       | events                       | ``CF``                                                 |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /events_by_sites/              | event_by_sites               | ``CF`` - ``update``                                    |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /events_by_buildings/          | event_by_buildings           | ``CF`` - ``update``                                    |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /events_by_storeys/            | event_by_storeys             | ``CF`` - ``update``                                    |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /events_by_spaces/             | event_by_spaces              | ``CF`` - ``update``                                    |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /events_by_zones/              | event_by_zones               | ``CF`` - ``update``                                    |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /event_categories/             | event_categories             | ``CF``                                                 |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /event_categories_by_users/    | event_categories_by_users    | ``CF``                                                 |
+--------------------------------+------------------------------+--------------------------------------------------------+
| /notifications/                | notifications                | ``CF``, ``count_by_campaign``, ``mark_all_as_read``    |
+--------------------------------+------------------------------+--------------------------------------------------------+


Tasks (services)
~~~~~~~~~~~~~~~~

+-------------------------+---------------------------+----------------------------------+
|      API resources      |  API client entry points  |  API client entry point actions  |
+=========================+===========================+==================================+
| /tasks/                 | tasks                     | ``getall``, ``run_async``        |
+-------------------------+---------------------------+----------------------------------+
| /tasks_by_campaigns/    | task_by_campaign          | ``CF``                           |
+-------------------------+---------------------------+----------------------------------+


Usage example
-------------

    Remember to rely on *API documentation*, as it fully describes all API endpoints: query arguments required, data format in payloads and responses content (status codes, data format...).

.. code:: python3

    import datetime as dt

    from bemserver_api_client import BEMServerApiClient
    from bemserver_api_client.enums import DegreeDaysPeriod
    from bemserver_api_client.exceptions import (
        BEMServerAPINotFoundError,
        BEMServerAPIValidationError,
    )

    # Get an instance of API client, setting the API host.
    api_client = BEMServerApiClient("localhost:5000")

    # Get the authentication bearer access and refresh tokens (JWT).
    auth_resp = api_client.auth.get_tokens("user@email.com", "password")
    if auth_resp.data["status"] == "failure":
        # User could not be authenticated (no access/refresh tokens are returned).
        # Raise exception, ...
        pass
    # At this point (auth_resp.data["status"] == "success"), the user is authenticated.
    #  auth_resp.data contains access and refresh tokens:
    #  {
    #      "status": "success",
    #      "access_token": "...",
    #      "refresh_token": "..."
    #  }

    # Set authentication method (bearer token authentication) in API client instance,
    #  in order to call private API endpoints.
    api_client.set_authentication_method(
        BEMServerApiClient.make_bearer_token_auth(
            auth_resp.data["access_token"], auth_resp.data["refresh_token"]
        )
    )

    # NOTE: When expired access token is automatically refreshed inside API client
    #  and requests goes on. Else `BEMServerAPIAuthenticationError` is raised and
    #  a new authentication is needed to continue calling private API endpoints.

    # Get a list of all the sites available (for the authenticated user).
    sites_resp = api_client.sites.getall()
    # sites_resp is an instance of `BEMServerApiClientResponse` class,
    #  which has processed yet API response data
    # sites_resp.data contains sites list:
    #  [
    #      {
    #          "id": 0,
    #          "name": "A",
    #          "latitude": -90,
    #          "longitude": -180,
    #          "description": "AAAAAA",
    #          "ifc_id": "AAAAAA",
    #          "campaign_id": 0
    #      }
    #  ]

    # Get the heating degree days data of a specific site.
    dd_resp = api_client.sites.get_degree_days(
        1,
        dt.date(2024, 1, 1).isoformat(),
        dt.date(2025, 1, 1).isoformat(),
        period=DegreeDaysPeriod.month,
    )
    # dd_resp.data contains:
    #  {
    #      "degree_days": {
    #          "2024-01-01T00:00:00+01:00": 76.05166666666668,
    #          "2024-02-01T00:00:00+01:00": 85.16583333333332,
    #          "2024-03-01T00:00:00+01:00": 65.69916666666667,
    #          "2024-04-01T00:00:00+02:00": 11.920000000000002,
    #          "2024-05-01T00:00:00+02:00": 0,
    #          "2024-06-01T00:00:00+02:00": 0,
    #          "2024-07-01T00:00:00+02:00": 0,
    #          "2024-08-01T00:00:00+02:00": 0,
    #          "2024-09-01T00:00:00+02:00": 0,
    #          "2024-10-01T00:00:00+02:00": 0,
    #          "2024-11-01T00:00:00+01:00": 2.098333333333331,
    #          "2024-12-01T00:00:00+01:00": null
    #      }
    #  }

    # Get a specific site, that does not exists (status code 404).
    # In this case, the API error response is processed and api client raises an exception.
    try:
        sites_resp = api_client.sites.getone(42)
    except BEMServerAPINotFoundError:
        # Manage resource not found error.
        pass

    # Some kind of errors, like BEMServerAPIValidationError, includes details on what occured.
    try:
        sites_resp = api_client.sites.create({"campaign_id": 1})
    except BEMServerAPIValidationError as exc:
        # Manage validation error.
        print(exc.errors)
        # exc.errors actually contains a dict of validation messages:
        #  {
        #      "name": [
        #          "Missing data for required field."
        #      ]
        #  }
