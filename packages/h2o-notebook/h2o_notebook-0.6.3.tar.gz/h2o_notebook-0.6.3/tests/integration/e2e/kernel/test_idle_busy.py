import datetime
import time

import pytest

from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from tests.integration.e2e.helper import wait_task_executing


@pytest.mark.timeout(900)
def test_kernel_idle(
    kernel_python_user: Kernel,
    kernel_client_user: KernelClient,
    kernel_task_client_user: KernelTaskClient,
):
    k: Kernel = kernel_python_user
    assert k.state == KernelState.STATE_STARTING

    kernel_task = kernel_task_client_user.create_kernel_task(
        parent=k.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="idle-1",
    )
    kernel_task_client_user.wait_task_completed(name=kernel_task.name)

    # After a first task has been completed, the kernel should be in the idle state
    # It takes once reconciliation loop to detect the idle state
    time.sleep(10)  # sleep for one reconciliation loop
    k = kernel_client_user.get_kernel(name=k.name)

    assert k.state == KernelState.STATE_RUNNING_IDLE
    assert k.current_task == ""
    assert k.current_task_sequence_number == 0
    assert k.task_queue_size == 0
    # last_activity_time is set somewhere between kernel start and now
    assert k.last_activity_time is not None
    assert k.last_activity_time > k.create_time
    assert k.last_activity_time < datetime.datetime.now(tz=datetime.timezone.utc)


@pytest.mark.timeout(900)
def test_kernel_busy(
    kernel_python_user: Kernel,
    kernel_client_user: KernelClient,
    kernel_task_client_user: KernelTaskClient,
):
    k: Kernel = kernel_python_user

    kernel_task = kernel_task_client_user.create_kernel_task(
        parent=k.name,
        kernel_task=KernelTask(
            code="""
            import time
            time.sleep(600)
            """,
        ),
        kernel_task_id="busy-1",
    )
    wait_task_executing(kernel_task_client_user, kernel_task=kernel_task)

    k = kernel_client_user.get_kernel(name=k.name)

    assert k.state == KernelState.STATE_RUNNING_BUSY
    assert k.current_task == kernel_task.name
    assert k.current_task_sequence_number == 2
    assert k.task_queue_size == 0
    # last_activity_time is set somewhere between kernel start and now
    assert k.last_activity_time is not None
    assert k.last_activity_time > k.create_time
    assert k.last_activity_time < datetime.datetime.now(tz=datetime.timezone.utc)
