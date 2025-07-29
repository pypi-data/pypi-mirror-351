import pprint
from typing import List

from h2o_notebook.clients.base.image_pull_policy import ImagePullPolicy
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.type import KernelImageType


class KernelImageConfig:
    """KernelImageConfig object used as input for apply method."""

    def __init__(
        self,
        kernel_image_id: str,
        kernel_image_type: KernelImageType,
        image: str,
        display_name: str,
        disabled: bool,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: List[str] = None,
    ):
        """
        Parameters are same as for KernelImage.
        """
        self.kernel_image_id = kernel_image_id
        self.display_name = display_name
        self.kernel_image_type = kernel_image_type
        self.image = image
        self.disabled = disabled
        self.image_pull_policy = image_pull_policy
        self.image_pull_secrets = image_pull_secrets

    def get_name(self):
        return f"{GLOBAL_WORKSPACE}/kernelImages/{self.kernel_image_id}"

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
