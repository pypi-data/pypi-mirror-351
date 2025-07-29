import pprint

from h2o_notebook.clients.kernel_template.kernel_template import from_api_object
from h2o_notebook.gen.model.v1_list_kernel_templates_response import (
    V1ListKernelTemplatesResponse,
)


class KernelTemplatesPage:
    """Class represents a list of KernelTemplates together with a next_page_token for listing all KernelTemplates."""

    def __init__(self, list_api_response: V1ListKernelTemplatesResponse) -> None:
        api_objects = list_api_response.kernel_templates
        self.kernel_templates = []
        for api_kernel_template in api_objects:
            self.kernel_templates.append(from_api_object(api_kernel_template))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
