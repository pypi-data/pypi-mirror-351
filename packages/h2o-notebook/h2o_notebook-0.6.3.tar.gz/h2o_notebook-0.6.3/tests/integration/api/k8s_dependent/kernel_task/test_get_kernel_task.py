import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from h2o_notebook.exception import CustomApiException


def test_get_kernel_task(
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

    kt_get = kernel_task_client_user.get_kernel_task(name=kt.name)
    assert kt_get.name == f"{kernel_user.name}/tasks/task1"
    assert kt_get.get_kernel_task_id() == "task1"
    assert kt_get.code == "print('Hello world!')"
    assert kt_get.state == KernelTaskState.STATE_QUEUED
    assert kt_get.sequence_number == 1
    assert kt_get.tasks_ahead_count == 0
    assert kt_get.error == ""
    assert kt_get.error_value == ""
    assert kt_get.traceback == ""
    assert kt_get.create_time is not None
    assert kt_get.execution_start_time is None
    assert kt_get.complete_time is None


def test_get_kernel_task_super_admin_not_found(kernel_task_client_super_admin):
    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_super_admin.get_kernel_task(
            name=f"{DEFAULT_WORKSPACE}/kernels/kernel-test-get/tasks/not-found",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_get_kernel_task_user_forbidden(
    kernel_super_admin: Kernel,
    kernel_task_client_super_admin,
    kernel_task_client_user,
):
    kt = kernel_task_client_super_admin.create_kernel_task(
        parent=f"{kernel_super_admin.name}",
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
    )

    # User cannot get kernel task of another users kernel.
    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_user.get_kernel_task(
            name=kt.name,
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
