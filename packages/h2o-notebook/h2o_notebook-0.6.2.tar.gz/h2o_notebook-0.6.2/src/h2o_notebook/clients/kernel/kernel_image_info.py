from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.clients.kernel_image.type import (
    from_api_object as from_kernel_image_type_api_object,
)
from h2o_notebook.gen.model.v1_kernel_image_info import V1KernelImageInfo


class KernelImageInfo:
    """
    KernelImageInfo contains data from the KernelImage that is used to create a Kernel.
    The original KernelImage might be deleted or modified during the lifetime of the Kernel.
    """

    def __init__(
        self,
        kernel_image_type: KernelImageType = KernelImageType.TYPE_UNSPECIFIED,
        image: str = "",
    ):
        """


        Args:
            kernel_image_type (KernelImageType, optional): Type of the KernelImage.
            image (str, optional): Docker image name.
        """
        self.kernel_image_type = kernel_image_type
        self.image = image

    def to_api_object(self) -> V1KernelImageInfo:
        return V1KernelImageInfo(
            image_type=self.kernel_image_type.to_api_object(),
            image=self.image,
        )


def from_api_object(api_object: V1KernelImageInfo) -> KernelImageInfo:
    return KernelImageInfo(
        kernel_image_type=from_kernel_image_type_api_object(api_object.kernel_image_type),
        image=api_object.image,
    )
