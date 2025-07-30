from typing import Optional

from h2o_notebook.clients.auth.token_api_client import TokenApiClient
from h2o_notebook.clients.connection_config import ConnectionConfig
from h2o_notebook.clients.kernel_task_output.kernel_task_output import KernelTaskOutput
from h2o_notebook.clients.kernel_task_output.kernel_task_output import from_api_object
from h2o_notebook.exception import CustomApiException
from h2o_notebook.gen import ApiException
from h2o_notebook.gen import Configuration
from h2o_notebook.gen.api.kernel_task_output_service_api import (
    KernelTaskOutputServiceApi,
)
from h2o_notebook.gen.model.v1_kernel_task_output import V1KernelTaskOutput


class KernelTaskOutputClient:
    """KernelTaskOutputClient manages Python kernel task messages."""

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
            self.api_instance = KernelTaskOutputServiceApi(api_client)

    def get_kernel_task_output(
        self,
        name: str,
    ) -> KernelTaskOutput:
        """
        Get KernelTaskOutput.

        Args:
            name (str): KernelTaskOutput resource name. Format is `workspaces/*/kernels/*/tasks/*/output`.

        Returns:
            KernelTaskOutput: KernelTaskOutput object.
        """
        api_object: V1KernelTaskOutput

        try:
            api_object = self.api_instance.kernel_task_output_service_get_kernel_task_output(
                name_2=name,
            ).kernel_task_output
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)
