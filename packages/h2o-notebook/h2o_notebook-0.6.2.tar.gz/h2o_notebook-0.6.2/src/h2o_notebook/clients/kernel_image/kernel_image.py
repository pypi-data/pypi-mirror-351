import pprint
from typing import List

from h2o_notebook.clients.base.image_pull_policy import ImagePullPolicy
from h2o_notebook.clients.base.image_pull_policy import (
    from_api_image_pull_policy_to_custom,
)
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.gen.model.required_kernel_image_resource import (
    RequiredKernelImageResource,
)
from h2o_notebook.gen.model.v1_kernel_image import V1KernelImage


class KernelImage:
    """
    KernelImage represents a Docker image that is used to run a kernel.
    """
    def __init__(
        self,
        kernel_image_type: KernelImageType,
        image: str,
        name: str = "",
        display_name: str = "",
        disabled: bool = False,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: List[str] = None,
    ):
        """
        Args:
            kernel_image_type (KernelImageType): KernelImage type.
            image (str): Docker image.
            name (str, optional): Resource name. Format is `workspaces/*/kernelImages/*`.
            disabled (bool, optional): Whether image is disabled.
            display_name (str, optional): Human-readable name of the KernelImage. Must contain at most 63 characters. Does not have to be unique.
            image_pull_policy (ImagePullPolicy, optional): Policy that determines how the Docker image
                for the KernelImage should be pulled. When unspecified, server will choose a default one.
            image_pull_secrets (List[str], optional): A list of Kubernetes secret references used for authenticating
                to private container registries or repositories.
                These secrets provide the necessary credentials to pull Docker images from private repositories.
                Each entry in this list should be the name of a Kubernetes secret configured in the cluster.
        """
        if image_pull_secrets is None:
            image_pull_secrets = []

        self.kernel_image_type = kernel_image_type
        self.image = image
        self.name = name
        self.display_name = display_name
        self.disabled = disabled
        self.image_pull_policy = image_pull_policy
        self.image_pull_secrets = image_pull_secrets

    def get_kernel_image_id(self) -> str:
        segments = self.name.split("/")
        if len(segments) != 4:
            return ""

        return segments[3]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1KernelImage:
        return V1KernelImage(
            display_name=self.display_name,
            type=self.kernel_image_type.to_api_object(),
            image=self.image,
            disabled=self.disabled,
            image_pull_policy=self.image_pull_policy.to_api_image_pull_policy(),
            image_pull_secrets=self.image_pull_secrets,
        )

    def to_resource(self) -> RequiredKernelImageResource:
        return RequiredKernelImageResource(
            display_name=self.display_name,
            type=self.kernel_image_type.to_api_object(),
            image=self.image,
            disabled=self.disabled,
            image_pull_policy=self.image_pull_policy.to_api_image_pull_policy(),
            image_pull_secrets=self.image_pull_secrets,
        )


def from_api_object(api_object: V1KernelImage) -> KernelImage:
    return KernelImage(
        name=api_object.name,
        kernel_image_type=KernelImageType(str(api_object.type)),
        image=api_object.image,
        display_name=api_object.display_name,
        disabled=api_object.disabled,
        image_pull_policy=from_api_image_pull_policy_to_custom(api_object.image_pull_policy),
        image_pull_secrets=api_object.image_pull_secrets,
    )
