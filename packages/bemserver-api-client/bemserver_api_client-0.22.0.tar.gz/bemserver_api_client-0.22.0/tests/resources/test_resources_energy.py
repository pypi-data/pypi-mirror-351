"""BEMServer API client energy resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.energy import (
    EnergyConsumptionTimseriesByBuildingResources,
    EnergyConsumptionTimseriesBySiteResources,
    EnergyEndUseResources,
    EnergyProductionTechnologyResources,
    EnergyProductionTimseriesByBuildingResources,
    EnergyProductionTimseriesBySiteResources,
    EnergyResources,
)


class TestAPIClientResourcesEnergies:
    def test_api_client_resources_energies(self):
        assert issubclass(EnergyResources, BaseResources)
        assert EnergyResources.endpoint_base_uri == "/energies/"
        assert EnergyResources.disabled_endpoints == [
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert EnergyResources.client_entrypoint == "energies"


class TestAPIClientResourcesEnergyEndUses:
    def test_api_client_resources_energy_end_uses(self):
        assert issubclass(EnergyEndUseResources, BaseResources)
        assert EnergyEndUseResources.endpoint_base_uri == "/energy_end_uses/"
        assert EnergyEndUseResources.disabled_endpoints == [
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert EnergyEndUseResources.client_entrypoint == "energy_end_uses"


class TestAPIClientResourcesEnergyConsumption:
    def test_api_client_resources_energy_consumption(self):
        assert issubclass(EnergyConsumptionTimseriesBySiteResources, BaseResources)
        assert EnergyConsumptionTimseriesBySiteResources.endpoint_base_uri == (
            "/energy_consumption_timeseries_by_sites/"
        )
        assert EnergyConsumptionTimseriesBySiteResources.disabled_endpoints == []
        assert EnergyConsumptionTimseriesBySiteResources.client_entrypoint == (
            "energy_cons_ts_by_sites"
        )

        assert issubclass(EnergyConsumptionTimseriesByBuildingResources, BaseResources)
        assert EnergyConsumptionTimseriesByBuildingResources.endpoint_base_uri == (
            "/energy_consumption_timeseries_by_buildings/"
        )
        assert EnergyConsumptionTimseriesByBuildingResources.disabled_endpoints == []
        assert EnergyConsumptionTimseriesByBuildingResources.client_entrypoint == (
            "energy_cons_ts_by_buildings"
        )


class TestAPIClientResourcesEnergyProductionTechnologies:
    def test_api_client_resources_energy_prod_technos(self):
        assert issubclass(EnergyProductionTechnologyResources, BaseResources)
        assert EnergyProductionTechnologyResources.endpoint_base_uri == (
            "/energy_production_technologies/"
        )
        assert EnergyProductionTechnologyResources.disabled_endpoints == [
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert EnergyProductionTechnologyResources.client_entrypoint == (
            "energy_prod_technologies"
        )


class TestAPIClientResourcesEnergyProduction:
    def test_api_client_resources_energy_production(self):
        assert issubclass(EnergyProductionTimseriesBySiteResources, BaseResources)
        assert EnergyProductionTimseriesBySiteResources.endpoint_base_uri == (
            "/energy_production_timeseries_by_sites/"
        )
        assert EnergyProductionTimseriesBySiteResources.disabled_endpoints == []
        assert EnergyProductionTimseriesBySiteResources.client_entrypoint == (
            "energy_prod_ts_by_sites"
        )

        assert issubclass(EnergyProductionTimseriesByBuildingResources, BaseResources)
        assert EnergyProductionTimseriesByBuildingResources.endpoint_base_uri == (
            "/energy_production_timeseries_by_buildings/"
        )
        assert EnergyProductionTimseriesByBuildingResources.disabled_endpoints == []
        assert EnergyProductionTimseriesByBuildingResources.client_entrypoint == (
            "energy_prod_ts_by_buildings"
        )
