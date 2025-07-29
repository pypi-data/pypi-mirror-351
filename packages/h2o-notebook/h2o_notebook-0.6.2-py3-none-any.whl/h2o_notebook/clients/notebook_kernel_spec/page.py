import pprint

from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec import (
    from_api_object,
)
from h2o_notebook.gen.model.v1_list_notebook_kernel_specs_response import (
    V1ListNotebookKernelSpecsResponse,
)


class NotebookKernelSpecsPage:
    """Class represents a list of NotebookKernelSpecs together with a next_page_token for listing all NotebookKernelSpecs."""

    def __init__(self, list_api_response: V1ListNotebookKernelSpecsResponse) -> None:
        api_objects = list_api_response.notebook_kernel_specs
        self.notebook_kernel_specs = []
        for api_notebook_kernel_spec in api_objects:
            self.notebook_kernel_specs.append(from_api_object(api_notebook_kernel_spec))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
