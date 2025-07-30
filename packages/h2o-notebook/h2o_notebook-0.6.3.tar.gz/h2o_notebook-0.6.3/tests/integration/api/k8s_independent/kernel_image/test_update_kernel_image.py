import http
import json

import pytest

from h2o_notebook.clients.base.image_pull_policy import ImagePullPolicy
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.client import KernelImageClient
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.exception import CustomApiException


def test_update_kernel_image(
    delete_all_kernel_images_before_after,
    kernel_image_client_super_admin: KernelImageClient,
    kernel_image_super_admin: KernelImage,
):
    kernel_image_super_admin.display_name = "new-name"
    kernel_image_super_admin.kernel_image_type = KernelImageType.TYPE_SPARK_R
    kernel_image_super_admin.image = "new-image"
    kernel_image_super_admin.disabled = True
    kernel_image_super_admin.image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    kernel_image_super_admin.image_pull_secrets = ["secret1"]

    updated = kernel_image_client_super_admin.update_kernel_image(
        kernel_image=kernel_image_super_admin,
    )

    assert updated.display_name == "new-name"
    assert updated.kernel_image_type == KernelImageType.TYPE_SPARK_R
    assert updated.image == "new-image"
    assert updated.disabled is True
    assert updated.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert updated.image_pull_secrets == ["secret1"]

    updated.display_name = "new-name-2"
    updated.disabled = False
    updated.image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_NEVER
    updated.image_pull_secrets = ["this", "will", "not", "be", "applied"]

    updated_again = kernel_image_client_super_admin.update_kernel_image(
        kernel_image=updated,
        update_mask="display_name,disabled,image_pull_policy",
    )

    assert updated_again.display_name == "new-name-2"
    assert updated_again.kernel_image_type == KernelImageType.TYPE_SPARK_R
    assert updated_again.image == "new-image"
    assert updated_again.disabled is False
    assert updated_again.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_NEVER
    assert updated_again.image_pull_secrets == ["secret1"]


def test_update_kernel_image_not_found(
    delete_all_kernel_images_before_after,
    kernel_image_client_super_admin: KernelImageClient,
    kernel_image_super_admin: KernelImage,
):
    kernel_image_super_admin.name = f"{GLOBAL_WORKSPACE}/kernelImages/whatever"
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_super_admin.update_kernel_image(
            kernel_image=kernel_image_super_admin,
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_update_kernel_image_client_validation(
    delete_all_kernel_images_before_after,
    kernel_image_client_super_admin: KernelImageClient,
    kernel_image_super_admin: KernelImage,
):
    kernel_image_super_admin.image = ""

    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_super_admin.update_kernel_image(
            kernel_image=kernel_image_super_admin,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'validation error: image must not be empty' in json.loads(exc.value.body)["message"]


def test_update_kernel_image_forbidden(
    delete_all_kernel_images_before_after,
    kernel_image_client_user: KernelImageClient,
    kernel_image_super_admin: KernelImage,
):
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_user.update_kernel_image(
            kernel_image=kernel_image_super_admin,
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
