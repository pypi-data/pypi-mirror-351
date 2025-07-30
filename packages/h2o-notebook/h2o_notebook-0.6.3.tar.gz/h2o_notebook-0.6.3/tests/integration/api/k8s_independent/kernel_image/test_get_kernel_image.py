import http

import pytest

from h2o_notebook.clients.base.image_pull_policy import ImagePullPolicy
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.exception import CustomApiException


def test_get_kernel_image_super_admin(kernel_image_super_admin, kernel_image_client_super_admin):
    # Admin can get any kernel image
    ki = kernel_image_client_super_admin.get_kernel_image(
        name=f"{GLOBAL_WORKSPACE}/kernelImages/kernel-image-super-admin",
    )

    assert ki.name == "workspaces/global/kernelImages/kernel-image-super-admin"
    assert ki.get_kernel_image_id() == "kernel-image-super-admin"
    assert ki.kernel_image_type == KernelImageType.TYPE_PYTHON
    assert ki.display_name == ""
    assert ki.disabled is False
    assert ki.image == "something"
    assert ki.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS
    assert ki.image_pull_secrets == []


def test_get_kernel_image_super_admin_not_found(kernel_image_client_super_admin):
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_super_admin.get_kernel_image(
            name=f"{GLOBAL_WORKSPACE}/kernelImages/non-existing",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_get_kernel_image_user(kernel_image_super_admin, kernel_image_client_user):
    # User can get any kernel image.
    ki = kernel_image_client_user.get_kernel_image(
        name=f"{GLOBAL_WORKSPACE}/kernelImages/kernel-image-super-admin",
    )

    assert ki.name == "workspaces/global/kernelImages/kernel-image-super-admin"
    assert ki.get_kernel_image_id() == "kernel-image-super-admin"
    assert ki.kernel_image_type == KernelImageType.TYPE_PYTHON
    assert ki.display_name == ""
    assert ki.disabled is False
    assert ki.image == "something"
    assert ki.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS
    assert ki.image_pull_secrets == []


def test_get_kernel_image_user_not_found(kernel_image_client_user):
    # User gets NOT_FOUND if KernelImage does not exist.
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_user.get_kernel_image(
            name=f"{GLOBAL_WORKSPACE}/kernelImages/kernel-image-super-admin",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
