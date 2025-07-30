import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel.type import KernelType
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.exception import CustomApiException


def test_get_kernel(
    kernel_client_user: KernelClient,
    kernel_image_session: KernelImage,
    kernel_template_session: KernelTemplate,
    delete_all_kernels_after,
):
    kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
        kernel_id="kernel-get",
    )

    k = kernel_client_user.get_kernel(name=f"{DEFAULT_WORKSPACE}/kernels/kernel-get")
    assert k.name == f"{DEFAULT_WORKSPACE}/kernels/kernel-get"
    assert k.get_kernel_id() == "kernel-get"
    assert k.state == KernelState.STATE_STARTING
    assert k.kernel_type == KernelType.TYPE_HEADLESS
    assert k.display_name == ""
    assert k.kernel_image == kernel_image_session.name
    assert k.kernel_template == kernel_template_session.name
    assert k.environmental_variables == {}
    assert k.creator != ""
    assert k.creator_display_name != ""
    assert k.current_task == ""
    assert k.current_task_sequence_number == 0
    assert k.task_queue_size == 0
    assert k.create_time is not None
    assert k.last_activity_time is None
    assert k.notebook_kernel_spec == ""


def test_get_kernel_forbidden(kernel_client_user: KernelClient):
    # User gets FORBIDDEN if Kernel does not exist.
    with pytest.raises(CustomApiException) as exc:
        kernel_client_user.get_kernel(name=f"{DEFAULT_WORKSPACE}/kernels/non-existing")
    assert exc.value.status == http.HTTPStatus.FORBIDDEN


def test_get_kernel_super_admin_not_found(kernel_client_super_admin: KernelClient):
    with pytest.raises(CustomApiException) as exc:
        kernel_client_super_admin.get_kernel(name=f"{DEFAULT_WORKSPACE}/kernels/non-existing")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
