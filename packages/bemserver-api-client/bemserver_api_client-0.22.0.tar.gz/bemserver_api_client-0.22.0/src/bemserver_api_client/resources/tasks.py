"""BEMServer API client resources

/tasks/ endpoints
/tasks_by_campaigns/ endpoints
"""

from .base import BaseResources


class TasksResources(BaseResources):
    endpoint_base_uri = "/tasks/"
    disabled_endpoints = ["getone", "create", "update", "delete"]
    client_entrypoint = "tasks"

    def run_async(self, payload):
        endpoint = f"{self.endpoint_base_uri}run"
        return self._req._execute("POST", endpoint, json=payload)


class TaskByCampaignResources(BaseResources):
    endpoint_base_uri = "/tasks_by_campaigns/"
    client_entrypoint = "task_by_campaign"
