import http
import time

import pytest

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from h2o_notebook.exception import CustomApiException


@pytest.mark.timeout(300)
def test_kernel_task_cancel_completed(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
):
    t = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code="print('Hello World 1!')"
        ),
        kernel_task_id="cancel-1",
    )

    kernel_task_client_user.wait_task_completed(name=t.name)

    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_user.cancel_kernel_task(name=t.name)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.timeout(900)
def test_kernel_task_cancel_skip_queued(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
):
    # Given
    t1 = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code="""
            import time
            time.sleep(10)
            """
        ),
        kernel_task_id="cancel-2",
    )
    t2 = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code="""
            import time
            time.sleep(600)
            """,
        ),
        kernel_task_id="cancel-3",
    )

    kernel_task_client_user.cancel_kernel_task(name=t2.name)

    t3 = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code="print('Hello World!')",
        ),
        kernel_task_id="cancel-4",
    )

    # When
    t3_completed = kernel_task_client_user.wait_task_completed(name=t3.name)

    t1_completed = kernel_task_client_user.get_kernel_task(name=t1.name)
    t2_completed = kernel_task_client_user.get_kernel_task(name=t2.name)

    # Then
    assert t1_completed.state == KernelTaskState.STATE_COMPLETE_SUCCESS
    assert t3_completed.state == KernelTaskState.STATE_COMPLETE_SUCCESS
    assert t2_completed.state == KernelTaskState.STATE_CANCELLED


@pytest.mark.timeout(60)
def test_kernel_task_cancel_in_progress(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
):
    t = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code="""
            import time
            print('Start')
            time.sleep(600)
            print('End')
            """,
        ),
        kernel_task_id="cancel-5",
    )

    while True:
        t = kernel_task_client_user.get_kernel_task(name=t.name)
        if t.state == KernelTaskState.STATE_EXECUTING:
            time.sleep(2)
            break

    kernel_task_client_user.cancel_kernel_task(name=t.name)

    t_completed = kernel_task_client_user.wait_task_completed(name=t.name)
    t_messages = kernel_task_client_user.list_all_kernel_task_messages(kernel_task_name=t.name)

    assert t_completed.state == KernelTaskState.STATE_CANCELLED
    assert len(t_messages) == 1
    assert t_messages[0].std_out == "Start\n"
