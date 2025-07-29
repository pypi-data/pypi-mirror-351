from typing import List
from typing import Optional

from h2o_notebook.clients.auth.token_api_client import TokenApiClient
from h2o_notebook.clients.connection_config import ConnectionConfig
from h2o_notebook.clients.kernel_task_message.kernel_task_message import (
    KernelTaskMessage,
)
from h2o_notebook.clients.kernel_task_message.page import KernelTaskMessagesPage
from h2o_notebook.exception import CustomApiException
from h2o_notebook.gen import ApiException
from h2o_notebook.gen import Configuration
from h2o_notebook.gen.api.kernel_task_message_service_api import (
    KernelTaskMessageServiceApi,
)
from h2o_notebook.gen.model.v1_list_kernel_task_messages_response import (
    V1ListKernelTaskMessagesResponse,
)


class KernelTaskMessageClient:
    """KernelTaskMessageClient manages Python kernel task messages."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        configuration = Configuration(host=connection_config.server_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
            configuration, connection_config.token_provider
        ) as api_client:
            self.api_instance = KernelTaskMessageServiceApi(api_client)

    def list_kernel_task_messages(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> KernelTaskMessagesPage:
        """Lists KernelTaskMessages.

        Args:
            parent (str): The resource name of the KernelTask to list KernelTaskMessages from.
                Format is `workspaces/*/kernels/*/tasks/*`.
            page_size (int): Maximum number of KernelTaskMessages to return in a response.
                If unspecified (or set to 0), at most 50 KernelTaskMessages will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the KernelTaskMessagesPage.

        Returns:
            KernelTaskMessagesPage: KernelTaskMessagesPage object.
        """
        list_response: V1ListKernelTaskMessagesResponse

        try:
            list_response = (
                self.api_instance.kernel_task_message_service_list_kernel_task_messages(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return KernelTaskMessagesPage(list_response)

    def list_all_kernel_task_messages(self, parent: str) -> List[KernelTaskMessage]:
        """ List all KernelTaskMessages.

        Args:
            parent (str): The resource name of the KernelTask to list KernelTaskMessages from.
                Format is `workspaces/*/kernels/*/tasks/*`.

        Returns:
            List of KernelTaskMessage.
        """
        all_kernel_task_messages: List[KernelTaskMessage] = []
        next_page_token = ""
        while True:
            kernel_task_message_list = self.list_kernel_task_messages(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
            )
            all_kernel_task_messages = all_kernel_task_messages + kernel_task_message_list.kernel_task_messages
            next_page_token = kernel_task_message_list.next_page_token
            if next_page_token == "":
                break

        return all_kernel_task_messages
