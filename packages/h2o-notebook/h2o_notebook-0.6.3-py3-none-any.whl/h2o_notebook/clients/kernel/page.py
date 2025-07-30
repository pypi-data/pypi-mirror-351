import pprint

from h2o_notebook.clients.kernel.kernel import from_api_object
from h2o_notebook.gen.model.v1_list_kernels_response import V1ListKernelsResponse


class KernelsPage:
    """Class represents a list of Kernels together with a next_page_token for listing all Kernels."""

    def __init__(self, list_api_response: V1ListKernelsResponse) -> None:
        api_objects = list_api_response.kernels
        self.kernels = []
        for api_kernel in api_objects:
            self.kernels.append(from_api_object(api_kernel))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
