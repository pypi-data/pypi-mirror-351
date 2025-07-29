import http

import pytest

from h2o_notebook.clients.base.image_pull_policy import ImagePullPolicy
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.exception import CustomApiException


def test_create_kernel_image_default_values(
    kernel_image_client_super_admin,
    delete_all_kernel_images_after,
):
    k = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="img1",
    )

    assert k.name == "workspaces/global/kernelImages/img1"
    assert k.get_kernel_image_id() == "img1"
    assert k.kernel_image_type == KernelImageType.TYPE_PYTHON
    assert k.display_name == ""
    assert k.disabled is False
    assert k.image == "something"
    assert k.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS
    assert k.image_pull_secrets == []


def test_create_kernel_image_full_params(
    kernel_image_client_super_admin,
    delete_all_kernel_images_after,
):
    k = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_SPARK_PYTHON,
            image="something",
            disabled=True,
            display_name="my first kernel image",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=["secret1", "secret2"],
        ),
        kernel_image_id="img2",
    )

    assert k.name == "workspaces/global/kernelImages/img2"
    assert k.get_kernel_image_id() == "img2"
    assert k.kernel_image_type == KernelImageType.TYPE_SPARK_PYTHON
    assert k.display_name == "my first kernel image"
    assert k.disabled is True
    assert k.image == "something"
    assert k.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert k.image_pull_secrets == ["secret1", "secret2"]


def test_create_kernel_image_already_exists(
    kernel_image_client_super_admin,
    delete_all_kernel_images_after,
):
    kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="img1",
    )

    with pytest.raises(CustomApiException) as exc:
        # Try to create KernelImage with the same ID.
        kernel_image_client_super_admin.create_kernel_image(
            parent=GLOBAL_WORKSPACE,
            kernel_image=KernelImage(
                kernel_image_type=KernelImageType.TYPE_R,
                image="something else",
            ),
            kernel_image_id="img1",
        )

    # grpc AlreadyExists == http Conflict 409
    assert exc.value.status == http.HTTPStatus.CONFLICT


def test_create_kernel_image_user(kernel_image_client_user, delete_all_kernel_images_after):
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_user.create_kernel_image(
            parent=GLOBAL_WORKSPACE,
            kernel_image=KernelImage(
                kernel_image_type=KernelImageType.TYPE_PYTHON,
                image="something",
            ),
            kernel_image_id="img1",
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
