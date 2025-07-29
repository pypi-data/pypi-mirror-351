import time
from time import sleep
from typing import List
from typing import Optional

from h2o_notebook.clients.auth.token_api_client import TokenApiClient
from h2o_notebook.clients.connection_config import ConnectionConfig
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.kernel_task import from_api_object
from h2o_notebook.clients.kernel_task.page import KernelTasksPage
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from h2o_notebook.clients.kernel_task_message.client import KernelTaskMessageClient
from h2o_notebook.clients.kernel_task_message.kernel_task_message import (
    KernelTaskMessage,
)
from h2o_notebook.clients.kernel_task_message.page import KernelTaskMessagesPage
from h2o_notebook.clients.kernel_task_output.client import KernelTaskOutputClient
from h2o_notebook.clients.kernel_task_output.kernel_task_output import KernelTaskOutput
from h2o_notebook.exception import CustomApiException
from h2o_notebook.exception import TimeoutException
from h2o_notebook.gen import ApiException
from h2o_notebook.gen import Configuration
from h2o_notebook.gen.api.kernel_task_service_api import KernelTaskServiceApi
from h2o_notebook.gen.model.v1_kernel_task import V1KernelTask
from h2o_notebook.gen.model.v1_list_kernel_tasks_response import (
    V1ListKernelTasksResponse,
)


class KernelTaskClient:
    """KernelTaskClient manages Python kernel tasks."""

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
            self.api_instance = KernelTaskServiceApi(api_client)

        self.kernel_task_message_client = KernelTaskMessageClient(connection_config=connection_config)
        self.kernel_task_output_client = KernelTaskOutputClient(connection_config=connection_config)

    def create_kernel_task(
        self,
        parent: str,
        kernel_task: KernelTask,
        kernel_task_id: str = "",
    ) -> KernelTask:
        """Creates a KernelTask.

        Args:
            parent (str): The resource name of the Kernel to create the KernelTask in.
                Format is `workspaces/*/kernels/*`.
            kernel_task (KernelTask): The KernelTask resource to create.
            kernel_task_id (str, optional): The ID to use for the KernelTask, which will become the final component
                of the image's resource name.
                If left unspecified, the server will generate a random value.
                This value must:
                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character

        Returns:
            KernelTask: KernelTask object.
        """
        created_api_object: V1KernelTask

        try:
            created_api_object = self.api_instance.kernel_task_service_create_kernel_task(
                parent=parent,
                kernel_task=kernel_task.to_api_object(),
                kernel_task_id=kernel_task_id,
            ).kernel_task
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_kernel_task(self, name: str) -> KernelTask:
        """Returns a KernelTask.

        Args:
            name (str): The name of the KernelTask. Format is `workspaces/*/kernels/*/tasks/*`.

        Returns:
            KernelTask: KernelTask object.
        """
        api_object: V1KernelTask

        try:
            api_object = self.api_instance.kernel_task_service_get_kernel_task(
                name_3=name,
            ).kernel_task
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def cancel_kernel_task(self, name: str):
        """Cancels a KernelTask.
        Args:
            name (str): The name of the KernelTask. Format is `workspaces/*/kernels/*/tasks/*`.
        """
        try:
            self.api_instance.kernel_task_service_cancel_kernel_task(
                name=name,
                body={},
            )
        except ApiException as e:
            raise CustomApiException(e)

    def list_kernel_tasks(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> KernelTasksPage:
        """Lists KernelTasks.

        Args:
            parent (str): The resource name of the Kernel to list KernelTasks from.
                Format is `workspaces/*/kernels/*`.
            page_size (int): Maximum number of KernelTasks to return in a response.
                If unspecified (or set to 0), at most 50 KernelTasks will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the KernelTasksPage.

        Returns:
            KernelTasksPage: KernelTasksPage object.
        """
        list_response: V1ListKernelTasksResponse

        try:
            list_response = (
                self.api_instance.kernel_task_service_list_kernel_tasks(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return KernelTasksPage(list_response)

    def list_all_kernel_tasks(self, parent: str) -> List[KernelTask]:
        """ List all KernelTasks.

        Args:
            parent (str): The resource name of the Kernel to list KernelTasks from.
                Format is `workspaces/*/kernels/*`.

        Returns:
            List of KernelTask.
        """
        all_kernel_tasks: List[KernelTask] = []
        next_page_token = ""
        while True:
            kernel_task_list = self.list_kernel_tasks(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
            )
            all_kernel_tasks = all_kernel_tasks + kernel_task_list.kernel_tasks
            next_page_token = kernel_task_list.next_page_token
            if next_page_token == "":
                break

        return all_kernel_tasks

    def list_kernel_task_messages(
        self,
        kernel_task_name: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> KernelTaskMessagesPage:
        """Lists KernelTaskMessages.

        Args:
            kernel_task_name (str): The resource name of the KernelTask to list KernelTaskMessages from.
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
        return self.kernel_task_message_client.list_kernel_task_messages(
            parent=kernel_task_name,
            page_size=page_size,
            page_token=page_token,
        )

    def list_all_kernel_task_messages(self, kernel_task_name: str) -> List[KernelTaskMessage]:
        """ List all KernelTaskMessages.

        Args:
            kernel_task_name (str): The resource name of the KernelTask to list KernelTaskMessages from.
                Format is `workspaces/*/kernels/*/tasks/*`.

        Returns:
            List of KernelTaskMessages.
        """
        return self.kernel_task_message_client.list_all_kernel_task_messages(parent=kernel_task_name)

    def get_kernel_task_output(self, kernel_task_name: str) -> KernelTaskOutput:
        """Get KernelTaskOutput.

        Args:
            kernel_task_name (str): KernelTask resource name. Format is `workspaces/*/kernels/*/tasks/*`.

        Returns:
            KernelTaskOutput: KernelTaskOutput from KernelTask.
        """
        return self.kernel_task_output_client.get_kernel_task_output(name=f"{kernel_task_name}/output")

    def wait_task_completed(
        self,
        name: str,
        timeout_seconds: Optional[float] = None,
    ) -> KernelTask:
        """
        Wait until the KernelTask is completed.

        Args:
            name (str): The name of the KernelTask. Format is `workspaces/*/kernels/*/tasks/*`.
            timeout_seconds (Optional[float], optional). Timeout in seconds. If not specified, will wait indefinitely.
        """

        start = time.time()

        while True:
            if timeout_seconds is not None and time.time() - start > timeout_seconds:
                raise TimeoutException()

            kernel_task = self.get_kernel_task(name=name)
            if kernel_task.state in [
                KernelTaskState.STATE_COMPLETE_SUCCESS,
                KernelTaskState.STATE_COMPLETE_ERROR,
                KernelTaskState.STATE_CANCELLED,
            ]:
                return kernel_task

            sleep(5)
