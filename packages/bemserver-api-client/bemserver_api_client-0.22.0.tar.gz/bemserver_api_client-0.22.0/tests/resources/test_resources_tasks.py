"""BEMServer API client tasks resources tests"""

from bemserver_api_client.resources.base import BaseResources
from bemserver_api_client.resources.tasks import (
    TaskByCampaignResources,
    TasksResources,
)
from bemserver_api_client.response import BEMServerApiClientResponse


class TestAPIClientResourcesTasks:
    def test_api_client_resources_tasks(self):
        assert issubclass(TasksResources, BaseResources)
        assert TasksResources.endpoint_base_uri == "/tasks/"
        assert TasksResources.disabled_endpoints == [
            "getone",
            "create",
            "update",
            "delete",
        ]
        assert TasksResources.client_entrypoint == "tasks"
        assert hasattr(TasksResources, "run_async")

    def test_api_client_resources_tasks_endpoints(self, mock_request):
        tasks_res = TasksResources(mock_request)

        payload = {
            "task_name": "Another task",
            "campaign_id": 666,
            "start_time": "2020-01-01T00:00:00.000Z",
            "end_time": "2020-02-01T00:00:00.000Z",
            "parameters": {
                "property1": None,
                "property2": None,
            },
        }

        resp = tasks_res.run_async(payload)
        assert isinstance(resp, BEMServerApiClientResponse)
        assert resp.status_code == 204
        assert resp.is_json
        assert resp.data == {}


class TestAPIClientResourcesTasksByCampaigns:
    def test_api_client_resources_task_by_campaign(self):
        assert issubclass(TaskByCampaignResources, BaseResources)
        assert TaskByCampaignResources.endpoint_base_uri == "/tasks_by_campaigns/"
        assert TaskByCampaignResources.disabled_endpoints == []
        assert TaskByCampaignResources.client_entrypoint == "task_by_campaign"
