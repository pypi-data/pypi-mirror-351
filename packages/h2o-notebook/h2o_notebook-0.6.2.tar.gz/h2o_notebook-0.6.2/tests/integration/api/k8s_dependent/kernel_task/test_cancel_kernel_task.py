import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from h2o_notebook.exception import CustomApiException


def test_cancel_kernel_task(
    kernel_user: Kernel,
    kernel_task_client_user
):
    kt = kernel_task_client_user.create_kernel_task(
        parent=kernel_user.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="task1",
    )

    kernel_task_client_user.cancel_kernel_task(name=kt.name)

    kt_get = kernel_task_client_user.get_kernel_task(name=kt.name)

    assert kt_get.state == KernelTaskState.STATE_CANCELLED


def test_cancel_kernel_task_not_found(kernel_task_client_super_admin):
    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_super_admin.get_kernel_task(
            name=f"{DEFAULT_WORKSPACE}/kernels/kernel-test-get/tasks/not-found",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_super_admin.get_kernel_task(
            name=f"{DEFAULT_WORKSPACE}/kernels/not-found/tasks/task1",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
