import pprint

from h2o_notebook.clients.kernel_image.kernel_image import from_api_object
from h2o_notebook.gen.model.v1_list_kernel_images_response import (
    V1ListKernelImagesResponse,
)


class KernelImagesPage:
    """Class represents a list of KernelImages together with a next_page_token for listing all KernelImages."""

    def __init__(self, list_api_response: V1ListKernelImagesResponse) -> None:
        api_objects = list_api_response.kernel_images
        self.kernel_images = []
        for api_kernel_image in api_objects:
            self.kernel_images.append(from_api_object(api_kernel_image))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
