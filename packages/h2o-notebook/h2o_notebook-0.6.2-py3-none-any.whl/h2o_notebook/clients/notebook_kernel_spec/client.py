from typing import List
from typing import Optional

from h2o_notebook.clients.auth.token_api_client import TokenApiClient
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.connection_config import ConnectionConfig
from h2o_notebook.clients.kernel_image.client import KernelImageClient
from h2o_notebook.clients.kernel_image.kernel_image_config import KernelImageConfig
from h2o_notebook.clients.kernel_template.client import KernelTemplateClient
from h2o_notebook.clients.kernel_template.kernel_template_config import (
    KernelTemplateConfig,
)
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec import (
    NotebookKernelSpec,
)
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec import (
    from_api_object,
)
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec_config import (
    NotebookKernelSpecConfig,
)
from h2o_notebook.clients.notebook_kernel_spec.page import NotebookKernelSpecsPage
from h2o_notebook.exception import CustomApiException
from h2o_notebook.gen import ApiException
from h2o_notebook.gen import Configuration
from h2o_notebook.gen.api.notebook_kernel_spec_service_api import (
    NotebookKernelSpecServiceApi,
)
from h2o_notebook.gen.model.v1_list_notebook_kernel_specs_response import (
    V1ListNotebookKernelSpecsResponse,
)
from h2o_notebook.gen.model.v1_notebook_kernel_spec import V1NotebookKernelSpec


class NotebookKernelSpecClient:
    """NotebookKernelSpecClient manages notebook kernel specs."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
        kernel_image_client: KernelImageClient = None,
        kernel_template_client: KernelTemplateClient = None,
    ):
        configuration = Configuration(host=connection_config.server_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert

        self.kernel_image_client = kernel_image_client
        self.kernel_template_client = kernel_template_client

        with TokenApiClient(
            configuration, connection_config.token_provider
        ) as api_client:
            self.api_instance = NotebookKernelSpecServiceApi(api_client)

    def create_notebook_kernel_spec(
        self,
        parent: str,
        notebook_kernel_spec: NotebookKernelSpec,
        notebook_kernel_spec_id: str,
    ) -> NotebookKernelSpec:
        """Creates a NotebookKernelSpec.

        Args:
            parent (str): The resource name of the workspace to associate with the NotebookKernelSpec.
                Format is `workspaces/*`.
            notebook_kernel_spec (NotebookKernelSpec): NotebookKernelSpec to create.
            notebook_kernel_spec_id (str): The ID to use for the NotebookKernelSpec,
                which will become the final component of the spec's resource name.
                This value must:
                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character

        Returns:
            NotebookKernelSpec: NotebookKernelSpec object.
        """
        created_api_object: V1NotebookKernelSpec

        try:
            created_api_object = self.api_instance.notebook_kernel_spec_service_create_notebook_kernel_spec(
                parent=parent,
                notebook_kernel_spec=notebook_kernel_spec.to_api_object(),
                notebook_kernel_spec_id=notebook_kernel_spec_id,
            ).notebook_kernel_spec
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_notebook_kernel_spec(self, name: str) -> NotebookKernelSpec:
        """Returns a NotebookKernelSpec.

        Args:
            name (str): Resource name of NotebookKernelSpec. Format is `workspaces/*/notebookKernelSpecs/*`.

        Returns:
            NotebookKernelSpec: NotebookKernelSpec object.
        """
        api_object: V1NotebookKernelSpec

        try:
            api_object = self.api_instance.notebook_kernel_spec_service_get_notebook_kernel_spec(
                name_5=name,
            ).notebook_kernel_spec
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_notebook_kernel_specs(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> NotebookKernelSpecsPage:
        """Lists NotebookKernelSpecs.

        Args:
            parent (str): The resource name of the workspace from which to list NotebookKernelSpec.
                Format is `workspaces/*`.
            page_size (int): Maximum number of NotebookKernelSpecs to return in a response.
                If unspecified (or set to 0), at most 50 NotebookKernelSpecs will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the NotebookKernelSpecsPage.

        Returns:
            NotebookKernelSpecsPage: NotebookKernelSpecsPage object.
        """
        list_response: V1ListNotebookKernelSpecsResponse

        try:
            list_response = (
                self.api_instance.notebook_kernel_spec_service_list_notebook_kernel_specs(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return NotebookKernelSpecsPage(list_response)

    def list_all_notebook_kernel_specs(self, parent: str) -> List[NotebookKernelSpec]:
        """ List all NotebookKernelSpecs.
        Args:
            parent (str): The resource name of the workspace from which to list NotebookKernelSpec.
                Format is `workspaces/*`.

        Returns:
            List of NotebookKernelSpec.
        """
        all_notebook_kernel_specs: List[NotebookKernelSpec] = []
        next_page_token = ""
        while True:
            notebook_kernel_spec_list = self.list_notebook_kernel_specs(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
            )
            all_notebook_kernel_specs = all_notebook_kernel_specs + notebook_kernel_spec_list.notebook_kernel_specs
            next_page_token = notebook_kernel_spec_list.next_page_token
            if next_page_token == "":
                break

        return all_notebook_kernel_specs

    def update_notebook_kernel_spec(
        self,
        notebook_kernel_spec: NotebookKernelSpec,
        update_mask: str = "*",
    ) -> NotebookKernelSpec:
        """Updates a NotebookKernelSpec.

        Args:
            notebook_kernel_spec (NotebookKernelSpec): NotebookKernelSpec object.
            update_mask (str): The field mask to use for the update.
                Allowed field paths are: {"display_name", "kernel_image", "kernel_template", "disabled"}.

                If not set, all fields will be updated.
                Defaults to "*".

        Returns:
            NotebookKernelSpec: Updated NotebookKernelSpec object.
        """
        updated_api_object: V1NotebookKernelSpec

        try:
            updated_api_object = (
                self.api_instance.notebook_kernel_spec_service_update_notebook_kernel_spec(
                    notebook_kernel_spec_name=notebook_kernel_spec.name,
                    update_mask=update_mask,
                    notebook_kernel_spec=notebook_kernel_spec.to_resource(),
                ).notebook_kernel_spec
            )
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_api_object)

    def apply_notebook_kernel_specs(
        self,
        notebook_kernel_spec_configs: List[NotebookKernelSpecConfig],
    ) -> List[NotebookKernelSpec]:
        self.delete_all_notebook_kernel_specs(parent=GLOBAL_WORKSPACE)

        created_notebook_kernel_specs: List[NotebookKernelSpec] = []

        for cfg in notebook_kernel_spec_configs:
            created_spec = self.create_notebook_kernel_spec(
                parent=GLOBAL_WORKSPACE,
                notebook_kernel_spec=NotebookKernelSpec(
                    kernel_image=cfg.kernel_image,
                    kernel_template=cfg.kernel_template,
                    display_name=cfg.display_name,
                    disabled=cfg.disabled,
                ),
                notebook_kernel_spec_id=cfg.notebook_kernel_spec_id,
            )
            created_notebook_kernel_specs.append(created_spec)

        # Order created notebook_kernel_spec from newest to oldest.
        created_notebook_kernel_specs.reverse()

        return created_notebook_kernel_specs

    def apply_kernel_images_templates_notebook_specs(
        self,
        kernel_image_configs: List[KernelImageConfig],
        kernel_template_configs: List[KernelTemplateConfig],
        notebook_kernel_spec_configs: List[NotebookKernelSpecConfig],
    ) -> List[NotebookKernelSpec]:
        """
        Set all KernelImages, KernelTemplates and NotebookKernelSpecs to a state defined in the arguments.
        Objects not specified in the arguments will be deleted.
        Objects specified in the arguments will be recreated with the new values.

        Args:
            kernel_image_configs: configuration of KernelImages that should be applied.
            kernel_template_configs: configuration of KernelTemplates that should be applied.
            notebook_kernel_spec_configs: configuration of NotebookKernelSpecs that should be applied.
        Returns: applied NotebookKernelSpecs
        """
        self.delete_all_notebook_kernel_specs(parent=GLOBAL_WORKSPACE)
        self.kernel_image_client.delete_all_kernel_images(parent=GLOBAL_WORKSPACE)
        self.kernel_template_client.delete_all_kernel_templates(parent=GLOBAL_WORKSPACE)

        self.kernel_image_client.apply_kernel_images(kernel_image_configs=kernel_image_configs)
        self.kernel_template_client.apply_global_kernel_templates(kernel_template_configs=kernel_template_configs)
        applied_specs = self.apply_notebook_kernel_specs(
            notebook_kernel_spec_configs=notebook_kernel_spec_configs,
        )

        return applied_specs

    def delete_notebook_kernel_spec(self, name: str) -> None:
        """Deletes a NotebookKernelSpec.

        Args:
            name (str): Resource name of NotebookKernelSpec. Format is `workspaces/*/notebookKernelSpecs/*`.
        """
        try:
            self.api_instance.notebook_kernel_spec_service_delete_notebook_kernel_spec(
                name_3=name,
            )
        except ApiException as e:
            raise CustomApiException(e)

    def delete_all_notebook_kernel_specs(self, parent: str) -> None:
        """
        Helper function for deleting all NotebookKernelSpecs.

        Args:
            parent (str): The resource name of the workspace from which to list NotebookKernelSpec.
                Format is `workspaces/*`.
        """
        for spec in self.list_all_notebook_kernel_specs(parent=parent):
            self.delete_notebook_kernel_spec(name=spec.name)
