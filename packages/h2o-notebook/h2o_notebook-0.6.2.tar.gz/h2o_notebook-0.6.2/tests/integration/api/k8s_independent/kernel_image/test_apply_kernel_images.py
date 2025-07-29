from typing import List

from h2o_notebook.clients.base.image_pull_policy import ImagePullPolicy
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.kernel_image_config import KernelImageConfig
from h2o_notebook.clients.kernel_image.type import KernelImageType


def test_apply_kernel_images(kernel_image_client_super_admin, delete_all_kernel_images_after):
    k1 = KernelImageConfig(
        kernel_image_id="img1",
        kernel_image_type=KernelImageType.TYPE_PYTHON,
        image="something1",
        display_name="",
        disabled=False,
    )
    k2 = KernelImageConfig(
        kernel_image_id="img2",
        kernel_image_type=KernelImageType.TYPE_PYTHON,
        image="something2",
        display_name="",
        disabled=False,
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_NEVER,
    )
    k3 = KernelImageConfig(
        kernel_image_id="img3",
        kernel_image_type=KernelImageType.TYPE_PYTHON,
        image="something3",
        display_name="",
        disabled=False,
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
        image_pull_secrets=["secret1", "secret2"],
    )

    configs = [k1, k2, k3]

    kernel_images = kernel_image_client_super_admin.apply_kernel_images(configs)

    want = [
        KernelImage(
            name="workspaces/global/kernelImages/img1",
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something1",
            display_name="",
            disabled=False,
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
            image_pull_secrets=[],
        ),
        KernelImage(
            name="workspaces/global/kernelImages/img2",
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something2",
            display_name="",
            disabled=False,
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_NEVER,
            image_pull_secrets=[],
        ),
        KernelImage(
            name="workspaces/global/kernelImages/img3",
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something3",
            display_name="",
            disabled=False,
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=["secret1", "secret2"],
        ),
    ]

    assert_kernel_images_equal(want, kernel_images)

    kernel_images = kernel_image_client_super_admin.list_all_kernel_images(
        parent=GLOBAL_WORKSPACE,
    )
    assert_kernel_images_equal(want, kernel_images)


def assert_kernel_images_equal(want: List[KernelImage], images: List[KernelImage]):
    assert len(want) == len(images)

    for i in range(len(want)):
        n = len(want) - i - 1

        assert want[i].name == images[n].name
        assert want[i].display_name == images[n].display_name
        assert want[i].kernel_image_type == images[n].kernel_image_type
        assert want[i].image == images[n].image
        assert want[i].disabled == images[n].disabled
        assert want[i].image_pull_policy == images[n].image_pull_policy
        assert want[i].image_pull_secrets == images[n].image_pull_secrets
