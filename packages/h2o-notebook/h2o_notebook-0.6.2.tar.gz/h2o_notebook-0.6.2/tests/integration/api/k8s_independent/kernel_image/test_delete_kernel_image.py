import http

import pytest

from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.exception import CustomApiException


def test_delete_kernel_image(kernel_image_client_super_admin, delete_all_kernel_images_after):
    k = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="img1",
    )

    kernel_image_client_super_admin.delete_kernel_image(name=k.name)

    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_super_admin.get_kernel_image(name=k.name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_delete_kernel_image_not_found(kernel_image_client_super_admin, delete_all_kernel_images_after):
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_super_admin.delete_kernel_image(name=f"{GLOBAL_WORKSPACE}/kernelImages/not-found")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_delete_kernel_image_user(kernel_image_client_user, kernel_image_client_super_admin):
    # When exists some KernelImage
    ki = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="img1",
    )

    # Then user cannot delete it
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_user.delete_kernel_image(name=ki.name)
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # User will get Unauthorized (FORBIDDEN) even for deleting non-existing KernelImage
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_user.delete_kernel_image(
            name=f"{GLOBAL_WORKSPACE}/kernelImages/non-existing",
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
