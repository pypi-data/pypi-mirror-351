from enum import Enum

from h2o_notebook.gen.model.v1_image_pull_policy import V1ImagePullPolicy


class ImagePullPolicy(Enum):
    IMAGE_PULL_POLICY_UNSPECIFIED = "IMAGE_PULL_POLICY_UNSPECIFIED"
    IMAGE_PULL_POLICY_ALWAYS = "IMAGE_PULL_POLICY_ALWAYS"
    IMAGE_PULL_POLICY_NEVER = "IMAGE_PULL_POLICY_NEVER"
    IMAGE_PULL_POLICY_IF_NOT_PRESENT = "IMAGE_PULL_POLICY_IF_NOT_PRESENT"

    def to_api_image_pull_policy(self) -> V1ImagePullPolicy:
        return V1ImagePullPolicy(self.name)


def from_api_image_pull_policy_to_custom(api_image_pull_policy: V1ImagePullPolicy) -> ImagePullPolicy:
    return ImagePullPolicy(str(api_image_pull_policy))
