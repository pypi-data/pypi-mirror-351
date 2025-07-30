import pprint

from h2o_notebook.clients.kernel_task.kernel_task import from_api_object
from h2o_notebook.gen.model.v1_list_kernel_tasks_response import (
    V1ListKernelTasksResponse,
)


class KernelTasksPage:
    """Class represents a list of KernelTasks together with a next_page_token for listing all KernelTasks."""

    def __init__(self, list_api_response: V1ListKernelTasksResponse) -> None:
        api_objects = list_api_response.kernel_tasks
        self.kernel_tasks = []
        for api_kernel_task in api_objects:
            self.kernel_tasks.append(from_api_object(api_kernel_task))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
