import pprint

from h2o_notebook.clients.kernel_task_message.kernel_task_message import from_api_object
from h2o_notebook.gen.model.v1_list_kernel_task_messages_response import (
    V1ListKernelTaskMessagesResponse,
)


class KernelTaskMessagesPage:
    """
    A list of KernelTaskMessages together with a next_page_token for listing all KernelTaskMessages.
    """

    def __init__(self, list_api_response: V1ListKernelTaskMessagesResponse) -> None:
        api_objects = list_api_response.kernel_task_messages
        self.kernel_task_messages = []
        for api_kernel_task_message in api_objects:
            self.kernel_task_messages.append(from_api_object(api_kernel_task_message))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
