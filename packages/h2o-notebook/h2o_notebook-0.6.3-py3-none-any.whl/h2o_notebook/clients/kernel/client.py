import time
from typing import List
from typing import Optional

from h2o_notebook.clients.auth.token_api_client import TokenApiClient
from h2o_notebook.clients.connection_config import ConnectionConfig
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.kernel import from_api_object
from h2o_notebook.clients.kernel.page import KernelsPage
from h2o_notebook.exception import CustomApiException
from h2o_notebook.exception import TimeoutException
from h2o_notebook.gen import ApiException
from h2o_notebook.gen import Configuration
from h2o_notebook.gen.api.kernel_service_api import KernelServiceApi
from h2o_notebook.gen.model.v1_kernel import V1Kernel
from h2o_notebook.gen.model.v1_list_kernels_response import V1ListKernelsResponse


class KernelClient:
    """KernelClient manages Python kernels."""

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
            self.api_instance = KernelServiceApi(api_client)

    def create_kernel(
        self,
        parent: str,
        kernel: Kernel,
        kernel_id: str = "",
    ) -> Kernel:
        """Creates a Kernel.

        Args:
            parent (str): The resource name of the workspace to associate with the Kernel.
                Format is `workspaces/*`.
            kernel (Kernel): Kernel to create.
            kernel_id (str, optional): The ID to use for the Kernel, which will become the final component
                of the kernel's resource name.
                If left unspecified, the server will generate one.
                This value must:
                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character

        Returns:
            Kernel: Kernel object.
        """
        created_api_object: V1Kernel

        try:
            created_api_object = self.api_instance.kernel_service_create_kernel(
                parent=parent,
                kernel=kernel.to_api_object(),
                kernel_id=kernel_id,
            ).kernel
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_kernel(self, name: str) -> Kernel:
        """Returns a Kernel.

        Args:
            name (str): The resource name of the Kernel. Format is `workspaces/*/kernels/*`.

        Returns:
            Kernel: Kernel object.
        """
        api_object: V1Kernel

        try:
            api_object = self.api_instance.kernel_service_get_kernel(
                name_1=name,
            ).kernel
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_kernels(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> KernelsPage:
        """Lists Kernels.

        Args:
            parent (str): The resource name of the workspace from which to list Kernels.
                Format is `workspaces/*`.
            page_size (int): Maximum number of Kernels to return in a response.
                If unspecified (or set to 0), at most 50 Kernels will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the KernelsPage.

        Returns:
            KernelsPage: KernelsPage object.
        """
        list_response: V1ListKernelsResponse

        try:
            list_response = (
                self.api_instance.kernel_service_list_kernels(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return KernelsPage(list_response)

    def list_all_kernels(self, parent: str) -> List[Kernel]:
        """ List all Kernels.

        Args:
            parent (str): The resource name of the workspace from which to list Kernels.
                Format is `workspaces/*`.

        Returns:
            List of Kernel.
        """
        all_kernels: List[Kernel] = []
        next_page_token = ""
        while True:
            kernel_list = self.list_kernels(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
            )
            all_kernels = all_kernels + kernel_list.kernels
            next_page_token = kernel_list.next_page_token
            if next_page_token == "":
                break

        return all_kernels

    def terminate_kernel(self, name: str) -> Kernel:
        """Terminates a Kernel.

        Args:
            name (str): The resource name of the Kernel. Format is `workspaces/*/kernels/*`.
        """
        api_object: V1Kernel

        try:
            api_object = self.api_instance.kernel_service_terminate_kernel(
                name=name,
                body={},
            ).kernel
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def delete_kernel(self, name: str) -> None:
        """Deletes a Kernel.

        Args:
            name (str): The resource name of the Kernel. Format is `workspaces/*/kernels/*`.
        """
        try:
            self.api_instance.kernel_service_delete_kernel(
                name_1=name,
            )
        except ApiException as e:
            raise CustomApiException(e)

    def wait_kernel_deleted(self, name: str, timeout_seconds: Optional[float] = None) -> None:
        """Waits for a Kernel to be deleted.

        Args:
            name (str): The resource name of the Kernel. Format is `workspaces/*/kernels/*`.
            timeout_seconds (float, optional): Timeout in seconds. If not specified, will wait indefinitely.
        """
        start = time.time()

        while True:
            if timeout_seconds is not None and time.time() - start > timeout_seconds:
                raise TimeoutException()

            try:
                self.get_kernel(name=name)
            except CustomApiException:
                return

            time.sleep(2)

    def delete_all_kernels(self, parent: str) -> None:
        """Helper function for deleting all Kernels.
        Args:
            parent (str): The resource name of the workspace from which to delete all Kernels.
                Format is `workspaces/*`.
        """
        for n in self.list_all_kernels(parent=parent):
            self.delete_kernel(n.name)

    def wait_all_kernels_deleted(self, parent: str, timeout_seconds: Optional[float] = None) -> None:
        """Waits for all Kernels to be deleted.

        Args:
            parent (str): The resource name of the workspace from which to delete all Kernels.
                Format is `workspaces/*`.
            timeout_seconds (float, optional): Timeout in seconds. If not specified, will wait indefinitely.
        """
        start = time.time()

        while True:
            if timeout_seconds is not None and time.time() - start > timeout_seconds:
                raise TimeoutException()

            kernels = self.list_all_kernels(parent=parent)
            if len(kernels) == 0:
                return

            time.sleep(2)
