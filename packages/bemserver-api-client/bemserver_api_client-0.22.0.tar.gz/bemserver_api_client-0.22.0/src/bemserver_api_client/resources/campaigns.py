"""BEMServer API client resources

/campaigns/ endpoints
/user_groups_by_campaigns/ endpoints
/campaign_scopes/ endpoints
/user_groups_by_campaign_scopes/ endpoints
"""

from .base import BaseResources


class CampaignResources(BaseResources):
    endpoint_base_uri = "/campaigns/"
    client_entrypoint = "campaigns"


class UserGroupByCampaignResources(BaseResources):
    endpoint_base_uri = "/user_groups_by_campaigns/"
    disabled_endpoints = ["update"]
    client_entrypoint = "user_groups_by_campaigns"


class CampaignScopeResources(BaseResources):
    endpoint_base_uri = "/campaign_scopes/"
    client_entrypoint = "campaign_scopes"


class UserGroupByCampaignScopeResources(BaseResources):
    endpoint_base_uri = "/user_groups_by_campaign_scopes/"
    disabled_endpoints = ["update"]
    client_entrypoint = "user_groups_by_campaign_scopes"
