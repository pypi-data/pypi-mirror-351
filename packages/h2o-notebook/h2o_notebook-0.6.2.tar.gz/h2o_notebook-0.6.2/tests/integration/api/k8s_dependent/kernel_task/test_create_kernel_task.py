import http

import pytest

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from h2o_notebook.exception import CustomApiException


def test_create_kernel_task(
    kernel_user: Kernel,
    kernel_task_client_user,
):
    kt = kernel_task_client_user.create_kernel_task(
        parent=kernel_user.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="task1",
    )

    assert kt.name == f"{kernel_user.name}/tasks/task1"
    assert kt.get_kernel_task_id() == "task1"
    assert kt.code == "print('Hello world!')"
    assert kt.state == KernelTaskState.STATE_QUEUED
    assert kt.sequence_number == 1
    assert kt.tasks_ahead_count == 0
    assert kt.error == ""
    assert kt.error_value == ""
    assert kt.traceback == ""
    assert kt.create_time is not None
    assert kt.execution_start_time is None
    assert kt.complete_time is None


def test_create_kernel_task_generate_id(
    kernel_user: Kernel,
    kernel_task_client_user,
):
    kt = kernel_task_client_user.create_kernel_task(
        parent=kernel_user.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
    )

    kt2 = kernel_task_client_user.create_kernel_task(
        parent=kernel_user.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
    )

    assert kt.get_kernel_task_id() != ""
    assert kt.get_kernel_task_id() != kt2.get_kernel_task_id()


def test_create_kernel_task_already_exists(
    kernel_user: Kernel,
    kernel_task_client_user,
):
    kernel_task_client_user.create_kernel_task(
        parent=kernel_user.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="task-exists",
    )

    with pytest.raises(CustomApiException) as exc:
        # Try to create KernelTask with the same ID.
        kernel_task_client_user.create_kernel_task(
            parent=kernel_user.name,
            kernel_task=KernelTask(
                code="print('Hello world!')",
            ),
            kernel_task_id="task-exists",
        )

    # grpc AlreadyExists == http Conflict 409
    assert exc.value.status == http.HTTPStatus.CONFLICT


def test_create_kernel_task_forbidden(
    kernel_super_admin: Kernel,
    kernel_task_client_user,
):
    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_user.create_kernel_task(
            parent=kernel_super_admin.name,
            kernel_task=KernelTask(
                code="print('Hello world!')",
            ),
        )

    assert exc.value.status == http.HTTPStatus.FORBIDDEN
