import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.exception import CustomApiException


def test_delete_kernel(
    kernel_client_user: KernelClient,
    kernel_image_session: KernelImage,
    kernel_template_session: KernelTemplate,
    delete_all_kernels_after,
):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )

    kernel_client_user.delete_kernel(name=k.name)
    kernel_client_user.wait_kernel_deleted(name=k.name)

    # User gets FORBIDDEN if Kernel does not exist.
    with pytest.raises(CustomApiException) as exc:
        kernel_client_user.get_kernel(name=k.name)
    assert exc.value.status == http.HTTPStatus.FORBIDDEN


def test_delete_kernel_forbidden(kernel_client_user: KernelClient, delete_all_kernels_after):
    # User gets FORBIDDEN if Kernel does not exist.
    with pytest.raises(CustomApiException) as exc:
        kernel_client_user.delete_kernel(name=f"{DEFAULT_WORKSPACE}/kernels/not-found")
    assert exc.value.status == http.HTTPStatus.FORBIDDEN


def test_delete_kernel_not_found(kernel_client_super_admin: KernelClient, delete_all_kernels_after):
    with pytest.raises(CustomApiException) as exc:
        kernel_client_super_admin.delete_kernel(name=f"{DEFAULT_WORKSPACE}/kernels/not-found")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
