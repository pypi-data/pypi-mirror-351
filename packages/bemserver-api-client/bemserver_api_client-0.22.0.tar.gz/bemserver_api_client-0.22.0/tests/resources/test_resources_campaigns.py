"""BEMServer API client campaigns resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.campaigns import (
    CampaignResources,
    CampaignScopeResources,
    UserGroupByCampaignResources,
    UserGroupByCampaignScopeResources,
)


class TestAPIClientResourcesCampaigns:
    def test_api_client_resources_campaigns(self):
        assert issubclass(CampaignResources, BaseResources)
        assert CampaignResources.endpoint_base_uri == "/campaigns/"
        assert CampaignResources.disabled_endpoints == []
        assert CampaignResources.client_entrypoint == "campaigns"

        assert issubclass(UserGroupByCampaignResources, BaseResources)
        assert UserGroupByCampaignResources.endpoint_base_uri == (
            "/user_groups_by_campaigns/"
        )
        assert UserGroupByCampaignResources.disabled_endpoints == ["update"]
        assert UserGroupByCampaignResources.client_entrypoint == (
            "user_groups_by_campaigns"
        )

        assert issubclass(CampaignScopeResources, BaseResources)
        assert CampaignScopeResources.endpoint_base_uri == "/campaign_scopes/"
        assert CampaignScopeResources.disabled_endpoints == []
        assert CampaignScopeResources.client_entrypoint == "campaign_scopes"

        assert issubclass(UserGroupByCampaignScopeResources, BaseResources)
        assert UserGroupByCampaignScopeResources.endpoint_base_uri == (
            "/user_groups_by_campaign_scopes/"
        )
        assert UserGroupByCampaignScopeResources.disabled_endpoints == ["update"]
        assert UserGroupByCampaignScopeResources.client_entrypoint == (
            "user_groups_by_campaign_scopes"
        )
