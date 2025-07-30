from typing import List
from typing import Optional

from h2o_notebook.clients.auth.token_api_client import TokenApiClient
from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.connection_config import ConnectionConfig
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.clients.kernel_template.kernel_template import from_api_object
from h2o_notebook.clients.kernel_template.kernel_template_config import (
    KernelTemplateConfig,
)
from h2o_notebook.clients.kernel_template.page import KernelTemplatesPage
from h2o_notebook.exception import CustomApiException
from h2o_notebook.gen import ApiException
from h2o_notebook.gen import Configuration
from h2o_notebook.gen.api.kernel_template_service_api import KernelTemplateServiceApi
from h2o_notebook.gen.model.v1_kernel_template import V1KernelTemplate
from h2o_notebook.gen.model.v1_list_kernel_templates_response import (
    V1ListKernelTemplatesResponse,
)


class KernelTemplateClient:
    """KernelTemplateClient manages Python kernel templates."""

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
            self.api_instance = KernelTemplateServiceApi(api_client)

    def create_kernel_template(
        self,
        parent: str,
        kernel_template: KernelTemplate,
        kernel_template_id: str,
    ) -> KernelTemplate:
        """Creates a KernelTemplate.

        Args:
            parent (str): The resource name of the workspace to associate with the KernelTemplate.
                Format is `workspaces/*`.
            kernel_template (KernelTemplate): KernelTemplate to create.
            kernel_template_id (str): The ID to use for the KernelTemplate, which will become
                the final component of the template's resource name.
                This value must:
                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character

        Returns:
            KernelTemplate: KernelTemplate object.
        """
        created_api_object: V1KernelTemplate

        try:
            created_api_object = self.api_instance.kernel_template_service_create_kernel_template(
                parent=parent,
                kernel_template=kernel_template.to_api_object(),
                kernel_template_id=kernel_template_id,
            ).kernel_template
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_kernel_template(self, name: str) -> KernelTemplate:
        """Returns a KernelTemplate.

        Args:
            name (str): Name of the KernelTemplate to retrieve. Format is `workspaces/*/kernelTemplates/*`

        Returns:
            KernelTemplate: KernelTemplate object.
        """
        api_object: V1KernelTemplate

        try:
            api_object = self.api_instance.kernel_template_service_get_kernel_template(
                name_4=name,
            ).kernel_template
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_kernel_templates(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> KernelTemplatesPage:
        """Lists KernelTemplates.

        Args:
            parent (str): The resource name of the workspace from which to list KernelTemplates.
                Format is `workspaces/*`.
            page_size (int): Maximum number of KernelTemplates to return in a response.
                If unspecified (or set to 0), at most 50 KernelTemplates will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the KernelTemplatesPage.

        Returns:
            KernelTemplatesPage: KernelTemplatesPage object.
        """
        list_response: V1ListKernelTemplatesResponse

        try:
            list_response = (
                self.api_instance.kernel_template_service_list_kernel_templates(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return KernelTemplatesPage(list_response)

    def list_all_kernel_templates(self, parent: str) -> List[KernelTemplate]:
        """ List all KernelTemplates.

        Args:
            parent (str): The resource name of the workspace from which to list KernelTemplates.
                Format is `workspaces/*`.

        Returns:
            List of KernelTemplate.
        """
        all_kernel_templates: List[KernelTemplate] = []
        next_page_token = ""
        while True:
            kernel_template_list = self.list_kernel_templates(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
            )
            all_kernel_templates = all_kernel_templates + kernel_template_list.kernel_templates
            next_page_token = kernel_template_list.next_page_token
            if next_page_token == "":
                break

        return all_kernel_templates

    def apply_global_kernel_templates(self, kernel_template_configs: List[KernelTemplateConfig]) -> List[KernelTemplate]:
        """
        Super-admin only.
        Set all KernelTemplates in a global workspace to a state defined in kernel_template_configs.
        KernelTemplates not specified in the kernel_template_configs will be deleted.
        KernelTemplates specified in the kernel_template_configs will be recreated with the new values.

        Args:
            kernel_template_configs: configuration of KernelTemplates that should be applied.
        Returns: applied KernelTemplates
        """
        return self.apply_kernel_templates(kernel_template_configs, parent=GLOBAL_WORKSPACE)

    def apply_default_kernel_templates(self, kernel_template_configs: List[KernelTemplateConfig]) -> List[KernelTemplate]:
        """
        Set all KernelTemplates in a default workspace to a state defined in kernel_template_configs.
        KernelTemplates not specified in the kernel_template_configs will be deleted.
        KernelTemplates specified in the kernel_template_configs will be recreated with the new values.

        Args:
            kernel_template_configs: configuration of KernelTemplates that should be applied.
        Returns: applied KernelTemplates
        """
        return self.apply_kernel_templates(kernel_template_configs, parent=DEFAULT_WORKSPACE)

    def apply_kernel_templates(self, kernel_template_configs: List[KernelTemplateConfig], parent: str) -> List[KernelTemplate]:
        """Helper function for applying KernelTemplates.
        """
        self.delete_all_kernel_templates(parent=parent)

        created_kernel_templates: List[KernelTemplate] = []

        for cfg in kernel_template_configs:
            created_template = self.create_kernel_template(
                parent=parent,
                kernel_template=KernelTemplate(
                    gpu=cfg.gpu,
                    memory_bytes_limit=cfg.memory_bytes_limit,
                    max_idle_duration=cfg.max_idle_duration,
                    environmental_variables=cfg.environmental_variables,
                    yaml_pod_template_spec=cfg.yaml_pod_template_spec,
                    gpu_resource=cfg.gpu_resource,
                    milli_cpu_request=cfg.milli_cpu_request,
                    milli_cpu_limit=cfg.milli_cpu_limit,
                    memory_bytes_request=cfg.memory_bytes_request,
                    storage_bytes=cfg.storage_bytes,
                    storage_class_name=cfg.storage_class_name,
                    disabled=cfg.disabled,
                ),
                kernel_template_id=cfg.kernel_template_id,
            )
            created_kernel_templates.append(created_template)

        # Order created kernel_templates from newest to oldest.
        created_kernel_templates.reverse()

        return created_kernel_templates

    def delete_kernel_template(self, name: str) -> None:
        """Deletes a KernelTemplate.

        Args:
            name (str): Name of the KernelTemplate to delete. Format is `workspaces/*/kernelTemplates/*`
        """
        try:
            self.api_instance.kernel_template_service_delete_kernel_template(
                name_2=name,
            )
        except ApiException as e:
            raise CustomApiException(e)

    def delete_all_kernel_templates(self, parent: str) -> None:
        """Helper function for deleting all KernelTemplates.
        """

        for template in self.list_all_kernel_templates(parent=parent):
            self.delete_kernel_template(name=template.name)
